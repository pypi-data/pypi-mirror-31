#!/usr/bin/env python3
#
# This file is part of Script of Scripts (sos), a workflow system
# for the execution of commands and scripts in different languages.
# Please visit https://github.com/vatlab/SOS for more information.
#
# Copyright (C) 2016 Bo Peng (bpeng@mdanderson.org)
##
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import sys
import os
import shlex
import keyword
import tempfile
import time
from sos.utils import env, _parse_error, get_traceback, load_config_files
from sos.sos_eval import SoS_exec
from sos._version import __version__
from sos.__main__ import get_run_parser
from sos.sos_script import SoS_Script
from sos.sos_syntax import SOS_KEYWORDS
from sos.sos_executor import Base_Executor, __null_func__
from sos.sos_syntax import SOS_SECTION_HEADER
from sos.target import file_target, UnknownTarget, RemovedTarget, UnavailableLock
from sos.sos_step import PendingTasks
from .sos_step import Interactive_Step_Executor


class Interactive_Executor(Base_Executor):
    '''Interactive executor called from by iPython Jupyter or Spyder'''
    def __init__(self, workflow=None, args=None, shared=None, config=None):
        # we actually do not have our own workflow, everything is passed from ipython
        # by nested = True we actually mean no new dictionary
        if env.config['sig_mode'] is None:
            env.config['sig_mode'] = 'ignore'
        Base_Executor.__init__(self, workflow=workflow, args=args, shared=shared, config=config)
        self.md5 = self.create_signature()
        if env.config['sig_mode'] != 'ignore':
            # We append to existing workflow files because some files are ignored and we
            # still wants their information.
            with open(os.path.join(env.exec_dir, '.sos', f'{self.md5}.sig'), 'a') as sig:
                sig.write(f'# workflow: {self.workflow.name}\n')
                # script is None because it is entered from notebook
                sig.write('# script: __interactive__\n')
                sig.write(f'# included: {",".join([x[1] for x in self.workflow.content.included])}\n')
                sig.write(f'# configuration: {self.config.get("config_file", "")}\n')
                sig.write(f'# start time: {time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())}\n')
                sig.write(self.sig_content)
                sig.write('# runtime signatures\n')

    def reset_dict(self):
        env.sos_dict.set('__null_func__', __null_func__)
        env.sos_dict.set('SOS_VERSION', __version__)
        env.sos_dict.set('__args__', self.args)
        if self.md5:
            env.sos_dict.set('__workflow_sig__', os.path.join(env.exec_dir, '.sos', f'{self.md5}.sig'))

        self._base_symbols = set(dir(__builtins__)) | set(env.sos_dict['sos_symbols_']) | set(SOS_KEYWORDS) | set(keyword.kwlist)
        self._base_symbols -= {'dynamic'}

        # load configuration files
        cfg = load_config_files(self.config['config_file'])
        # if check_readonly is set to True, allow checking readonly vars
        if cfg.get('sos', {}).get('change_all_cap_vars', None) is not None:
            if cfg['sos']['change_all_cap_vars'] not in ('warning', 'error'):
                env.logger.error(
                    f'Configuration sos.change_all_cap_vars can only be warning or error: {cfg["sos"]["change_all_cap_vars"]} provided')
            else:
                env.sos_dict._change_all_cap_vars = cfg['sos']['change_all_cap_vars']
        env.sos_dict.set('CONFIG', cfg)
        # set config to CONFIG
        file_target('config.yml').remove('both')

        # remove some variables because they would interfere with step analysis
        for key in ('_input', 'input'):
            if key in env.sos_dict:
                env.sos_dict.pop(key)

        env.sos_dict.quick_update(self.shared)

        if isinstance(self.args, dict):
            for key, value in self.args.items():
                if not key.startswith('__'):
                    env.sos_dict.set(key, value)

    def run(self, targets=None, parent_pipe=None, my_workflow_id=None, mode='run'):
        '''Execute a block of SoS script that is sent by iPython/Jupyer/Spyer
        The code can be simple SoS/Python statements, one SoS step, or more
        or more SoS workflows with multiple steps. This executor,
        1. adds a section header to the script if there is no section head
        2. execute the workflow in interactive mode, which is different from
           batch mode in a number of ways, which most notably without support
           for nested workflow.
        3. Optionally execute the workflow in preparation mode for debugging purposes.
        '''
        # if there is no valid code do nothing
        self.reset_dict()

        # this is the result returned by the workflow, if the
        # last stement is an expression.
        last_res = None

        # process step of the pipelinp
        if isinstance(targets, str):
            targets = [targets]
        dag = self.initialize_dag(targets=targets)
        #
        # if targets are specified and there are only signatures for them, we need
        # to remove the signature and really generate them
        if targets:
            for t in targets:
                if not file_target(t).exists('target') and file_target(t).exists('signature'):
                    env.logger.debug(f'Re-generating {t}')
                    file_target(t).remove('signature')
                else:
                    env.logger.debug(f'Target {t} already exists')
        #
        while True:
            # find any step that can be executed and run it, and update the DAT
            # with status.
            runnable = dag.find_executable()
            if runnable is None:
                # no runnable
                #dag.show_nodes()
                break
            # find the section from runnable
            section = self.workflow.section_by_id(runnable._step_uuid)
            #
            # this is to keep compatibility of dag run with sequential run because
            # in sequential run, we evaluate global section of each step in
            # order to determine values of options such as skip.
            # The consequence is that global definitions are available in
            # SoS namespace.
            try:
                SoS_exec(section.global_def)
            except Exception as e:
                if env.verbosity > 2:
                    sys.stderr.write(get_traceback())
                raise RuntimeError(f'Failed to execute statements\n"{section.global_def}"\n{e}')

            # clear existing keys, otherwise the results from some random result
            # might mess with the execution of another step that does not define input
            for k in ['__step_input__', '__default_output__', '__step_output__']:
                if k in env.sos_dict:
                    env.sos_dict.pop(k)
            # if the step has its own context
            env.sos_dict.quick_update(runnable._context)
            # execute section with specified input
            runnable._status = 'running'
            try:
                executor = Interactive_Step_Executor(section)
                res = executor.run()
                for k, v in res.items():
                    env.sos_dict.set(k, v)
                last_res = res['__last_res__']
                # set context to the next logic step.
                for edge in dag.out_edges(runnable):
                    node = edge[1]
                    # if node is the logical next step...
                    if node._node_index is not None and runnable._node_index is not None:
                        #and node._node_index == runnable._node_index + 1:
                        node._context.update(env.sos_dict.clone_selected_vars(
                            node._context['__signature_vars__'] | node._context['__environ_vars__'] \
                            | {'_input', '__step_output__', '__default_output__', '__args__'}))
                    node._context['__completed__'].append(res['__step_name__'])
                runnable._status = 'completed'
            except (UnknownTarget, RemovedTarget) as e:
                runnable._status = None
                target = e.target
                if dag.regenerate_target(target):
                    #runnable._depends_targets.append(target)
                    #dag._all_dependent_files[target].append(runnable)
                    dag.build(self.workflow.auxiliary_sections)
                    #
                    cycle = dag.circular_dependencies()
                    if cycle:
                        raise RuntimeError(
                            f'Circular dependency detected {cycle} after regeneration. It is likely a later step produces input of a previous step.')

                else:
                    if self.resolve_dangling_targets(dag, [target]) == 0:
                        raise RuntimeError(
                            f'Failed to regenerate or resolve {target}{dag.steps_depending_on(target, self.workflow)}.')
                    runnable._depends_targets.append(target)
                    dag._all_dependent_files[target].append(runnable)
                    dag.build(self.workflow.auxiliary_sections)
                    #
                    cycle = dag.circular_dependencies()
                    if cycle:
                        raise RuntimeError(
                            f'Circular dependency detected {cycle}. It is likely a later step produces input of a previous step.')
                self.save_dag(dag)
            except UnavailableLock as e:
                runnable._status = 'pending'
                runnable._signature = (e.output, e.sig_file)
                env.logger.debug(f'Waiting on another process for step {section.step_name()}')
            except PendingTasks as e:
                self.record_quit_status(e.tasks)
                raise
            # if the job is failed
            except Exception as e:
                runnable._status = 'failed'
                raise
        if self.md5:
            self.save_workflow_signature(dag)
            env.logger.debug(f'Workflow {self.workflow.name} (ID={self.md5}) is executed successfully.')
        # remove task pending status if the workflow is completed normally
        try:
            wf_status = os.path.join(os.path.expanduser('~'), '.sos', self.md5 + '.status')
            if os.path.isfile(wf_status):
                os.remove(wf_status)
        except Exception as e:
            env.logger.warning(f'Failed to clear workflow status file: {e}')
        return last_res

#
# function runfile that is used by spyder to execute complete script
#

def runfile(script=None, raw_args='', wdir='.', code=None, kernel=None, **kwargs):
    # this has something to do with Prefix matching rule of parse_known_args
    #
    # That is to say
    #
    #   --rep 3
    #
    # would be parsed as
    #
    #   args.workflow=3, unknown --rep
    #
    # instead of
    #
    #   args.workflow=None, unknown --rep 3
    #
    # we then have to change the parse to disable args.workflow when
    # there is no workflow option.
    args = shlex.split(raw_args) if isinstance(raw_args, str) else raw_args
    if (script is None and code is None) or '-h' in args:
        parser = get_run_parser(interactive=True, with_workflow=True)
        parser.print_help()
        return
    if args and args[0].lstrip().startswith('-'):
        parser = get_run_parser(interactive=True, with_workflow=False)
        parser.error = _parse_error
        args, workflow_args = parser.parse_known_args(args)
        args.workflow = None
    else:
        parser = get_run_parser(interactive=True, with_workflow=True)
        parser.error = _parse_error
        args, workflow_args = parser.parse_known_args(args)

    # no multi-processing in interactive mode
    env.max_jobs = 1
    env.verbosity = args.verbosity

    if args.__queue__ == '':
        from sos.hosts import list_queues
        list_queues(args.__config__, args.verbosity)
        return

    if args.__remote__:
        from sos.utils import load_config_files
        cfg = load_config_files(args.__config__)
        env.sos_dict.set('CONFIG', cfg)
        if args.__remote__ == '':
            from .hosts import list_queues
            list_queues(cfg, args.verbosity)
            return

        # if executing on a remote host...
        from sos.hosts import Host
        host = Host(args.__remote__)
        #
        if script is None:
            if not code.strip():
                return
            script = os.path.join('.sos', '__interactive__.sos')
            with open(script, 'w') as s:
                s.write(code)

        # copy script to remote host...
        host.send_to_host(script)
        from sos.utils import remove_arg
        argv = shlex.split(raw_args) if isinstance(raw_args, str) else raw_args
        argv = remove_arg(argv, '-r')
        argv = remove_arg(argv, '-c')
        # execute the command on remote host
        try:
            with kernel.redirect_sos_io():
                ret = host._host_agent.run_command(['sos', 'run', script] + argv, wait_for_task=True,
                    realtime=True)
            if ret:
               kernel.send_response(kernel.iopub_socket, 'stream',
                                    dict(name='stderr',
                                         text=f'remote execution of workflow exited with code {ret}'))
        except Exception as e:
            if kernel:
                kernel.send_response(kernel.iopub_socket, 'stream',
                    {'name': 'stdout', 'text': str(e)})
        return

    if args.__bin_dirs__:
        import fasteners
        for d in args.__bin_dirs__:
            if d == '~/.sos/bin' and not os.path.isdir(os.path.expanduser(d)):
                with fasteners.InterProcessLock(os.path.join(tempfile.gettempdir(), 'sos_lock_bin')):
                    os.makedirs(os.path.expanduser(d))
            elif not os.path.isdir(os.path.expanduser(d)):
                raise ValueError(f'directory does not exist: {d}')
        os.environ['PATH'] = os.pathsep.join([os.path.expanduser(x) for x in args.__bin_dirs__]) + os.pathsep + os.environ['PATH']

    # clear __step_input__, __step_output__ etc because there is
    # no concept of passing input/outputs across cells.
    env.sos_dict.set('__step_output__', [])
    for k in ['__step_input__', '__default_output__', 'input', 'output', \
        'depends', '_input', '_output', '_depends']:
        env.sos_dict.pop(k, None)

    try:
        if script is None:
            if not code.strip():
                return
            if kernel is None:
                script = SoS_Script(content=code)
            else:
                if kernel._workflow_mode:
                    # in workflow mode, the content is sent by magics %run and %sosrun
                    script = SoS_Script(content=code)
                else:
                    # this is a scratch step...
                    # if there is no section header, add a header so that the block
                    # appears to be a SoS script with one section
                    if not any([SOS_SECTION_HEADER.match(line) or line.startswith('%from') or line.startswith('%include') for line in code.splitlines()]):
                        code = '[scratch_0]\n' + code
                        script = SoS_Script(content=code)
                    else:
                        if kernel.cell_idx == -1:
                            kernel.send_frontend_msg('stream',
                                {'name': 'stdout', 'text': 'Workflow can only be executed with magic %run or %sosrun.'})
                        return
        else:
            script = SoS_Script(filename=script)
        workflow = script.workflow(args.workflow)
        executor = Interactive_Executor(workflow, args=workflow_args, config={
            'config_file': args.__config__,
            'output_dag': args.__dag__,
            'sig_mode': args.__sig_mode__,
            'default_queue': '' if args.__queue__ is None else args.__queue__,
            'wait_for_task': True if args.__wait__ is True or args.dryrun else (False if args.__no_wait__ else None),
            'resume_mode': kernel is not None and kernel._resume_execution,
            'run_mode': 'dryrun' if args.dryrun else 'interactive',
            'verbosity': args.verbosity,

            # wait if -w or in dryrun mode, not wait if -W, otherwise use queue default
            'max_procs': 1,
            'max_running_jobs': args.__max_running_jobs__,
            # for infomration and resume only
            'workdir': os.getcwd(),
            'script': "interactive",
            'workflow': args.workflow,
            'targets': args.__targets__,
            'bin_dirs': args.__bin_dirs__,
            'workflow_args': workflow_args
        })
        return executor.run(args.__targets__)
    except PendingTasks:
        raise
    except SystemExit:
        # this happens because the executor is in resume mode but nothing
        # needs to be resumed, we simply pass
        return
    except Exception:
        if args.verbosity and args.verbosity > 2:
            sys.stderr.write(get_traceback())
        raise
    finally:
        env.config['sig_mode'] = 'ignore'
        env.verbosity = 2


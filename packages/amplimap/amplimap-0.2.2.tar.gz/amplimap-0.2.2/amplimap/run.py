#!/usr/bin/env python
import os
import sys

import snakemake
import argparse
import yaml

from .version import __title__, __version__

def check_config_keys(default_config, my_config, path = []):
    """Recursively check that config keys provided in my_config also exist in default_config (ignoring 'paths' and 'clusters')."""
    differences = []
    for key, value in my_config.items():
        if key in default_config:
            if isinstance(default_config[key], dict) == isinstance(value, dict):
                if isinstance(default_config[key], dict):
                    #both are dicts, keep checking
                    #but don't check paths/cluster because they can contain custom values
                    if not (len(path) == 0 and key in ['paths', 'clusters']):
                        differences += check_config_keys(default_config[key], value, path + [key])
                else:
                    #we're done here
                    pass
            else:
                differences.append(path + [key])
                #raise Exception('Config setting {} is invalid\n'.format(':'.join(path+[key])))
        else:
            differences.append(path + [key])
    return differences

def compare_config_dicts(my_config, used_config, path = []):
    """Recursively search for differences in values between two dicts."""
    differences = []
    for key, value in my_config.items():
        if key in used_config:
            if isinstance(value, dict):
                differences += compare_config_dicts(value, used_config[key], path + [key])
            else:
                if value != used_config[key]:
                    differences.append(path + [key])
        else:
            #key does not exist in used config
            sys.stderr.write('Warning - config key {} not set in used config\n'.format(':'.join(path+[key])))
    return differences

def main():
    """
    Run amplimap.
    """
    try:
        basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        #sys.stderr.write('Called with arguments: "{}"\n'.format('" "'.join(sys.argv)))
        
        #parse the arguments, which will be available as properties of args (e.g. args.probe)
        parser = argparse.ArgumentParser(
            description = "amplimap v{} - amplicon mapping and analysis pipeline".format(__version__),
            formatter_class = argparse.ArgumentDefaultsHelpFormatter)
        #specify parameters
        parser.add_argument("-v", "--version", help="print version and exit", action="store_true")
        parser.add_argument("--basedir", help="print basedir and exit", action="store_true")
        parser.add_argument("--print-config", help="print configuration (including global and local settings) and exit", action="store_true")
        parser.add_argument("-r", "--run", help="actually run (will perform a dry run otherwise)", action="store_true")
        parser.add_argument("--resume", help="resume analysis in existing analysis directory", action="store_true")
        parser.add_argument("--cluster", help="specify a cluster type defined in your configuration files to run jobs on cluster.")
        parser.add_argument("--skip-file-check", help="skip check for changes in input files when resuming (not recommended)", action="store_true")
        parser.add_argument("--unlock", help="unlock working directory", action="store_true")
        parser.add_argument("--working-directory", help="path to the working directory", default=".")
        parser.add_argument("--ncores", help="number of local cores to run in parallel (only applies if --cluster is NOT set)", default=1, type=int)
        parser.add_argument("--njobs", help="number of cluster jobs to run in parallel (only applies if --cluster is set)", default=10, type=int)
        parser.add_argument("--debug", help="debug mode", action="store_true")
        #parser.add_argument("--debug-dag", help="debug DAG", action="store_true")
        parser.add_argument("TARGET", help="targets to run (eg. pileups variants coverages)", nargs="*")
        args = parser.parse_args()

        if args.version:
            print('{} {}'.format(__title__, __version__))
            return 0

        if args.basedir:
            print(basedir)
            return 0

        #read default config to get cluster paths etc
        default_config = {}
        default_config_path = os.path.join(basedir, 'config_default.yaml')
        if args.print_config:
            sys.stderr.write('Reading default configuration from: {}\n'.format(default_config_path))
        if os.path.isfile(default_config_path):
            with open(default_config_path, 'r') as config_file:
                default_config = yaml.safe_load(config_file.read())
        else:
            raise Exception('config_default.yaml file missing!')

        #override with data from /etc/amplimap, if exists
        etc_config = {}
        etc_config_path = '/etc/amplimap/%s/config.yaml' % __version__
        if os.path.isfile(etc_config_path):
            if args.print_config:
                sys.stderr.write('Reading additional configuration from: {}\n'.format(etc_config_path))
            with open(etc_config_path, 'r') as config_file:
                etc_config = yaml.safe_load(config_file.read())

        #override with data from $AMPLIMAP_CONFIG, if exists
        env_config = {}
        try:
            env_config_path = os.environ['AMPLIMAP_CONFIG']
            if os.path.isfile(env_config_path):
                if args.print_config:
                    sys.stderr.write('Reading additional configuration from: {}\n'.format(env_config_path))
                with open(env_config_path, 'r') as config_file:
                    env_config = yaml.safe_load(config_file.read())
        except KeyError:
            pass

        #read local config
        local_config = {}
        local_config_path = os.path.join(args.working_directory, 'config.yaml')
        if os.path.isfile(local_config_path):
            with open(local_config_path, 'r') as config_file:
                local_config = yaml.safe_load(config_file.read())
        else:
            sys.stderr.write('No local config.yaml found, using default configuration.\n')

        #merge configs together
        config = default_config
        for my_config in [etc_config, env_config, local_config]:
            #check that all settings actually exist
            differences = check_config_keys(default_config, my_config)
            if len(differences) > 0:
                sys.stderr.write('Your configuration file(s) contain unknown or invalid settings:\n')
                for diff in differences:
                    sys.stderr.write('\t- {}\n'.format(':'.join(diff)))
                sys.stderr.write('Please check their spelling and location and try again.\n')
                return 1

            snakemake.utils.update_config(config, my_config)

        if args.print_config:
            yaml.dump(config, sys.stdout, default_flow_style=False)
            return 0

        #do some basic checks
        assert os.path.isdir(args.working_directory), 'working directory does not exist'
        assert os.path.isdir(os.path.join(args.working_directory, 'reads_in')) \
            or os.path.isdir(os.path.join(args.working_directory, 'bams_in')) \
            or os.path.isdir(os.path.join(args.working_directory, 'tagged_bams_in')) \
            or os.path.isdir(os.path.join(args.working_directory, 'unmapped_bams_in')), 'reads_in/, bams_in/ or unmapped_bams_in/ directory missing'
        # assert os.path.isfile(os.path.join(args.working_directory, 'probes.csv')) \
        #     or os.path.isfile(os.path.join(args.working_directory, 'probes_mipgen.csv')) \
        #     or os.path.isfile(os.path.join(args.working_directory, 'probes_heatseq.tsv')), 'probes.csv, probes_mipgen.csv, or probes_heatseq.tsv file missing'

        #check some basic settings
        if not config['general']['reference_type'] in ['genome', 'transcriptome']:
            raise Exception('general: reference_type must be genome or transcriptome!')

        aligners = ['naive', 'bwa', 'bowtie2', 'star']
        if not config['align']['aligner'] in aligners:
            raise Exception('align: aligner must be one of {}!'.format(','.join(aligners)))

        callers = ['gatk', 'platypus']
        if not config['variants']['caller'] in callers:
            raise Exception('variants: caller must be one of {}!'.format(','.join(callers)))

        if config['general']['quality_trim_threshold'] != False:
            if not isinstance(config['general']['quality_trim_threshold'], float):
                raise Exception('quality_trim_threshold must be a decimal number!')
            if not config['general']['quality_trim_threshold'] > 0 and config['general']['quality_trim_threshold'] < 1:
                raise Exception('quality_trim_threshold must be either "false" or above 0 and below 1!')

        if not config['parse_reads']['min_percentage_good'] >= 0 and config['parse_reads']['min_percentage_good'] <= 100:
            raise Exception('min_percentage_good must be between 0 and 100')

        if config['annotate']['annovar']['protocols'].count(',') != config['annotate']['annovar']['operations'].count(','):
            raise Exception('The number of comma-separated protocols and operations under `annotate: annovar:` must match!')

        #check we have proper paths
        if not config['general']['genome_name'] in config['paths']:
            raise Exception('Could not find list of paths for genome_name: "{}". Please add the paths to your default configuration or your local config.yaml file.'.format(config['general']['genome_name']))

        for name, path in config['paths'][config['general']['genome_name']].items():
            if path.startswith('/PATH/TO/'):
                raise Exception('Path for {} reference is set to {}, which is probably incorrect. Please set the correct path in your default configuration or your local config.yaml file, or leave it empty.'.format(
                    name, path))

        #adjust config
        config['general']['basedir'] = basedir
        config['general']['amplimap_dir'] = os.path.join(basedir, 'amplimap')

        #check if analysis dir exists already
        analysis_dir = os.path.join(args.working_directory, 'analysis')
        configfile = os.path.join(analysis_dir, 'config_used.yaml')
        used_versions_path = os.path.join(analysis_dir, 'versions.yaml')

        #the analysis dir may exist just because we did a dry run, but once the versions exist we actually executed snakemake!
        if os.path.exists(analysis_dir) and os.path.exists(used_versions_path):
            if not args.resume:
                raise Exception('An analysis directory already exists. Please rename it or set --resume to reuse it and possibly overwrite existing files.')
            else:
                #check version
                if os.path.isfile(used_versions_path):
                    with open(used_versions_path, 'r') as used_versions_file:
                        used_versions = yaml.safe_load(used_versions_file.read())
                        if used_versions['_amplimap'] != str(__version__):
                            sys.stderr.write('This analysis was performed with {} {} but this is {} {}!\n\n'.format(__title__, used_versions['_amplimap'], __title__, __version__))
                            sys.stderr.write('Please use the correct version of {} or start a new analysis.\n'.format(__title__))
                            return 1
                        else:
                            sys.stderr.write('{} version checked.\n'.format(__title__))

                #check used config file
                if os.path.isfile(configfile):
                    with open(configfile, 'r') as used_config_file:
                        used_config = yaml.safe_load(used_config_file.read())
                        differences = compare_config_dicts(config, used_config)
                        if len(differences) > 0:
                            sys.stderr.write('config_used.yaml in analysis directory differs from current config.yaml in working directory! Please rename or delete the old analysis directory to restart analysis with the new configuration.\n')
                            sys.stderr.write('Different settings:\n')
                            for diff in differences:
                                sys.stderr.write('\t- {}\n'.format(':'.join(diff)))
                            return 1
                        else:
                            sys.stderr.write('Config files checked.\n')

                #check hashes of input files
                if not args.skip_file_check:
                    used_file_hashes_path = os.path.join(analysis_dir, 'file_hashes.yaml')
                    if os.path.isfile(used_file_hashes_path):
                        with open(used_file_hashes_path, 'r') as used_file_hashes_file:
                            used_file_hashes = yaml.safe_load(used_file_hashes_file.read())

                            from .reader import get_file_hashes
                            for fn, current_hash in get_file_hashes().items():
                                if used_file_hashes[fn] != current_hash:
                                    sys.stderr.write('File {} seems to have changed since the last run!\n\n'.format(fn))
                                    sys.stderr.write('To ensure consistent results, you should rename or delete the old analysis directory and start a new analysis.\n')
                                    sys.stderr.write('To ignore this error, add the --skip-file-check parameter.\n')
                                    return 1
                            sys.stderr.write('Input files checked.\n')
                else:
                    sys.stderr.write('Warning: Skipping input file check.\n')

        #ensure analysis dir exists now
        try:
            os.makedirs(analysis_dir)
        except OSError as e:
            pass

        #write config to analysis directory, and then use that for snakemake
        with open(configfile, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)

        #set up cluster commands
        cluster_command_nosync = None
        cluster_command_sync = None

        if args.cluster:
            if args.cluster in config['clusters']:
                if 'command_sync' in config['clusters'][args.cluster]:
                    cluster_command_sync = config['clusters'][args.cluster]['command_sync']
                elif 'command_nosync' in config['clusters'][args.cluster]:
                    cluster_command_nosync = config['clusters'][args.cluster]['command_nosync']
                else:
                    raise Exception('Invalid cluster configuration -- need either command_sync or command_nosync for: {}'.format(args.cluster))
            else:
                raise Exception('Cluster type not found in config: {}'.format(args.cluster))

            sys.stderr.write('Running in cluster mode {} with {} parallel jobs\n'.format(args.cluster, args.njobs))
            sys.stderr.write('cluster_command_nosync={}\n'.format(cluster_command_nosync))
            sys.stderr.write('cluster_command_sync={}\n'.format(cluster_command_sync))

            #make sure cluster log directory exists (this assumed the cluster command is using this as a parameter)
            cluster_logs = os.path.join(args.working_directory, 'cluster_log')
            try:
                os.makedirs(cluster_logs)
            except OSError as e:
                pass
            sys.stderr.write('Will write cluster logs to: {}\n'.format(cluster_logs))
        else:
            sys.stderr.write('Running locally with {} cores\n'.format(args.ncores))

        success = snakemake.snakemake(
            snakefile = os.path.join(basedir, "Snakefile"),
            configfile = configfile,
            cores = args.ncores, #ignored if cluster
            nodes = args.njobs, #ignored if not cluster
            workdir = args.working_directory,
            targets = args.TARGET,
            dryrun = not args.run,
            cluster = cluster_command_nosync,
            cluster_sync = cluster_command_sync,
            jobname = "{}.{{rulename}}.{{jobid}}.sh".format(__title__),
            unlock = args.unlock,
            #debug_dag = args.debug_dag,
            )

        if success:
            if args.unlock:
                sys.stderr.write('Unlocked working directory. Run without --unlock to start.\n')
            elif not args.run:
                sys.stderr.write('{} {} dry run successful. Set --run to run!\n'.format(__title__,  __version__))
            else:
                sys.stderr.write('{} {} finished!\n'.format(__title__, __version__))
            return 0
        else:
            sys.stderr.write('{} {} failed! Please see output above or cluster logs for details.\n'.format(__title__,  __version__))
            return 1
    except Exception as e:
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.stderr.write('\nERROR: {}\n\n'.format(e))
        return 1

if __name__ == '__main__':
    sys.exit(main())
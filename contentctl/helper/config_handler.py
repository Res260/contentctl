import os
import collections
import sys
import pathlib

from contentctl.input.yml_reader import YmlReader
from contentctl.objects.config import Config, TestConfig
from contentctl.objects.enums import DetectionTestingMode
from typing import Union
import argparse

class ConfigHandler:

    @classmethod
    def read_config(cls, args:argparse.Namespace) -> Config:
        config_path = pathlib.Path(args.path)/"contentctl.yml"
        try:
            yml_dict = YmlReader.load_file(config_path, add_fields=False)

        except:
            print("ERROR: no contentctl.yml found in given path")
            sys.exit(1)

        try: 
            config = Config.parse_obj(yml_dict)
        except Exception as e:
            raise Exception(f"Error reading config file: {str(e)}")
            

        return config
    
    @classmethod
    def read_test_config(cls, args:argparse.Namespace) -> TestConfig:
        test_config_path = pathlib.Path(args.path)/"contentctl_test.yml"
        try:
            yml_dict = YmlReader.load_file(test_config_path, add_fields=False)
        except:
            print("ERROR: no contentctl_test.yml found in given path")
            sys.exit(1)

        try: 
            if args.dry_run:
                yml_dict['apps'] = []
            if args.mode != DetectionTestingMode.changes:
                yml_dict['version_control_config'] = None
            if yml_dict.get("version_control_config", None) is not None:
                #If they have been passed, override the target and test branch. If not, keep the defaults
                yml_dict.get("version_control_config", None)['target_branch'] = args.target_branch or yml_dict.get("version_control_config", None)['target_branch']
                yml_dict.get("version_control_config", None)['test_branch'] = args.test_branch or yml_dict.get("version_control_config", None)['test_branch']
            if yml_dict.get("infrastructure_config", None) is not None:
                yml_dict.get("infrastructure_config", None)['infrastructure_type'] = args.infrastructure or yml_dict.get("infrastructure_config", None)['infrastructure_type']
            test_config = TestConfig.parse_obj(yml_dict)
        except Exception as e:
            raise Exception(f"Error reading test config file: {str(e)}")
            

        return test_config
    

          
 
 
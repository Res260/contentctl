import sys
import pathlib
from pydantic import ValidationError

from contentctl.input.yml_reader import YmlReader
from contentctl.objects.baseline import Baseline
from contentctl.objects.enums import SecurityContentType
from contentctl.objects.enums import SecurityContentProduct
from contentctl.input.director import DirectorOutputDto

class BaselineBuilder():
    baseline : Baseline

    def setObject(self, path: str, 
        output_dto:DirectorOutputDto) -> None:
        yml_dict = YmlReader.load_file(path)
        self.baseline = Baseline.model_validate(yml_dict, context={"output_dto":output_dto})



    def addDeployment(self, deployments: list) -> None:
        if not self.baseline.deployment:

            matched_deployments = []

            for d in deployments:
                d_tags = dict(d.tags)
                baseline_dict = self.baseline.dict()
                baseline_tags_dict = self.baseline.tags.dict()
                for d_tag in d_tags.keys():
                    for attr in baseline_dict.keys():
                        if attr == d_tag:
                            if isinstance(baseline_dict[attr], str):
                                if baseline_dict[attr] == d_tags[d_tag]:
                                    matched_deployments.append(d)
                            elif isinstance(baseline_dict[attr], list):
                                if d_tags[d_tag] in baseline_dict[attr]:
                                    matched_deployments.append(d)

                    for attr in baseline_tags_dict.keys():
                        if attr == d_tag:
                            if isinstance(baseline_tags_dict[attr], str):
                                if baseline_tags_dict[attr] == d_tags[d_tag]:
                                    matched_deployments.append(d)
                            elif isinstance(baseline_tags_dict[attr], list):
                                if d_tags[d_tag] in baseline_tags_dict[attr]:
                                    matched_deployments.append(d)

            if len(matched_deployments) == 0:
                raise ValueError('No deployment found for baseline: ' + self.baseline.name)

            self.baseline.deployment = matched_deployments[-1]


    def reset(self) -> None:
        self.baseline = None


    def getObject(self) -> Baseline:
        return self.baseline
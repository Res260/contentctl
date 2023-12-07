import os
import json


from contentctl.output.json_writer import JsonWriter
from contentctl.objects.enums import SecurityContentType

# Maximum Lambda Request Response Limit it 6MB
# https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html
AWS_LAMBDA_LIMIT = 1024 * 1024 * 6 - 1

class ApiJsonOutput():


 def checkMaxJsonObjectSize(self, output_path:str, 
                            max_size=AWS_LAMBDA_LIMIT,
                            size_warning_percent:float = .8,
                            file_names:list[str] = ['detections.json', 
                                                    'macros.json', 
                                                    'stories.json', 
                                                    'baselines.json', 
                                                    'response_tasks.json', 
                                                    'lookups.json', 
                                                    'deployments.json'])->None:
    # If size exceeds 90 percent of the maximum allowed size, throw a warning
    size_warning = round(max_size * size_warning_percent)
    exceptions = []
    warnings = []
    for file_name in file_names:
        file_path = os.path.join(output_path, file_name)
        size = os.path.getsize(file_path)
        if size >= max_size:
            exceptions.append(f"\n -{file_name}: {size} bytes")
        elif size >= size_warning:
            percent_of_maximum_size = round(size / max_size, 2) * 100
            print(f"WARNING: '{file_name}' is in danger of exceeding {max_size} bytes and is "
                  f"currently {percent_of_maximum_size}% of the maximum size. "
                  "Exceeding this limit will cause an error when hosting on AWS Lambda.")
    
    if len(exceptions) > 0:
        size_error_message = f"ERROR: The following files exceed the maximum JSON File size of {max_size} bytes:\n -{''.join(exceptions)}"
        raise(Exception(size_error_message))
    return     
 
 def writeObjects(self, objects: list, output_path: str, type: SecurityContentType = None) -> None:
        if type == SecurityContentType.detections:
            obj_array = []
            for detection in objects:
                detection.id = str(detection.id)
                obj_array.append(detection.dict(exclude_none=True, 
                    exclude =
                    {
                        "deprecated": True,
                        "experimental": True,
                        "annotations": True,
                        "risk": True,
                        "playbooks": True,
                        "baselines": True,
                        "mappings": True,
                        "test": True,
                        "deployment": True,
                        "type": True,
                        "status": True,
                        "data_source": True,
                        "tests": True,
                        "cve_enrichment": True,
                        "tags": 
                            {
                                "file_path": True,
                                "required_fields": True,
                                "confidence": True,
                                "impact": True,
                                "product": True,
                                "cve": True
                            }
                    }
                ))
            
            JsonWriter.writeJsonObject(os.path.join(output_path, 'detections.json'), {'detections': obj_array })

            ### Code to be added to contentctl to ship filter macros to macros.json

            obj_array = []    
            for detection in objects:
                detection_dict = detection.dict()
                if "macros" in detection_dict:
                    for macro in detection_dict["macros"]:
                        obj_array.append(macro)

            uniques:set[str] = set()
            for obj in obj_array:
                if obj.get("arguments",None) != None:
                    uniques.add(json.dumps(obj,sort_keys=True))
                else:
                    obj.pop("arguments")
                    uniques.add(json.dumps(obj, sort_keys=True))

            obj_array = []
            for item in uniques:
                obj_array.append(json.loads(item))

            JsonWriter.writeJsonObject(os.path.join(output_path, 'macros.json'), {'macros': obj_array})

        
        elif type == SecurityContentType.stories:
            obj_array = []
            for story in objects:
                story.id = str(story.id)
                obj_array.append(story.dict(exclude_none=True,
                    exclude =
                    {
                        "investigations": True
                    }
                ))

            JsonWriter.writeJsonObject(os.path.join(output_path, 'stories.json'), {'stories': obj_array })

        elif type == SecurityContentType.baselines:
            obj_array = []
            for baseline in objects:
                baseline.id = str(baseline.id)
                obj_array.append(baseline.dict(
                    exclude =
                    {
                        "deployment": True,
                        "check_references":True,
                        "file_path":True,
                    }
                ))

            JsonWriter.writeJsonObject(os.path.join(output_path, 'baselines.json'), {'baselines': obj_array })

        elif type == SecurityContentType.investigations:
            obj_array = []
            for investigation in objects:
                investigation.id = str(investigation.id)
                obj_array.append(investigation.dict(exclude_none=True))

            JsonWriter.writeJsonObject(os.path.join(output_path, 'response_tasks.json'), {'response_tasks': obj_array })
        
        elif type == SecurityContentType.lookups:
            obj_array = []
            for lookup in objects:

                obj_array.append(lookup.dict(exclude_none=True))


            JsonWriter.writeJsonObject(os.path.join(output_path, 'lookups.json'), {'lookups': obj_array })


        elif type == SecurityContentType.deployments:
            obj_array = []
            for deployment in objects:
                deployment.id = str(deployment.id)
                obj_array.append(deployment.dict(exclude_none=True, exclude =
                    {
                        "file_path":True,
                    }))

            JsonWriter.writeJsonObject(os.path.join(output_path, 'deployments.json'), {'deployments': obj_array })

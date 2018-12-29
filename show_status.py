# -*- coding: utf-8 -*-
from tencentcloud.common import credential
from tencentcloud.cvm.v20170312 import cvm_client, models as cvm_models

from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
import json

id="AKIDa2KQjrfxlQuIVWg7jBRIxQhmfNtEmMAp"
key="c2HKNEtNgqqfJm2Gg0BE8rOk05zjIjzM"
region="ap-hongkong"

cred = credential.Credential(id, key)
cvm_client = cvm_client.CvmClient(cred, region)
cvm_id= 'ins-3il1o098'

def show_cvm_info(cvm_id):
    try:
        #cvm_params = {"InstanceIds.N": [cvm_id]}
        filter_params = {"Filters": [{"Name": "instance-id", "Values": [cvm_id]}]}
        req = cvm_models.DescribeInstancesStatusRequest()
        req.from_json_string(json.dumps(filter_params))

        resp = cvm_client.DescribeInstancesStatus(req)
        cvm_info = json.loads(resp.to_json_string())["InstanceStatusSet"][0]["InstanceState"]
        return cvm_info
    except TencentCloudSDKException as err:
        print err
		
print show_cvm_info(cvm_id)
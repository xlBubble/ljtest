#!/bin/python3.5
#usage: stop cvm in guangzhou region by cvm id
#date:2018-12-03 17:52:37
#by:xul

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException 
from tencentcloud.cvm.v20170312 import cvm_client, models 
import json
import subprocess



def get_cvmid():

	try: 
	    req = models.DescribeInstancesRequest()
	    params = '{}'
	    req.from_json_string(params)

	    resp = client.DescribeInstances(req) 
	    return resp.to_json_string()

	except TencentCloudSDKException as err: 
	    print(err)
	    return 1


def main():

	cvm_item=[]
	INFO=json.loads(get_cvmid())
	temp=INFO['InstanceSet'] 
	for item in temp :
		#print ( item['InstanceId'] )
		#cvm_item.append(item['InstanceId'])
		stop_cvm(item['InstanceId'])
	#print (cvm_item)
	return 0

def stop_cvm(cvmid):
	try:
		req = models.StopInstancesRequest()
		temp = {"InstanceIds":[cvmid]}
		params = json.dumps(temp)
		req.from_json_string(params)
		
		resp = client.StopInstances(req) 
		return resp.to_json_string()

	except:
		print (err)
		return -1	

if __name__ == "__main__":
	cred = credential.Credential("AKIDa2KQjrfxlQuIVWg7jBRIxQhmfNtEmMAp", "c2HKNEtNgqqfJm2Gg0BE8rOk05zjIjzM")
	httpProfile = HttpProfile()
	httpProfile.endpoint = "cvm.ap-guangzhou.tencentcloudapi.com"

	clientProfile = ClientProfile()
	clientProfile.httpProfile = httpProfile
	client = cvm_client.CvmClient(cred, "ap-guangzhou", clientProfile)

	main()



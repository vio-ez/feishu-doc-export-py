
import os 
import json
import requests 
from urllib.parse import unquote 

import lark_oapi as lark
from lark_oapi.api.drive.v1 import *
from lark_oapi.api.wiki.v2 import *
from lark_oapi.api.sheets.v3 import * 

from config import *
 

APP_ID = 'cli_a7386447101e5013'
APP_SECRET = 'kJT3RxcH...awbDuE5qqefZr'

def log_response_err(response):
    lark.logger.error(
        f"client.wiki.v2.space.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")

class FeishuAdmin(object):
    def __init__(self):
        self.client = lark.Client.builder() \
        .app_id(APP_ID) \
        .app_secret(APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

        self.t_access_token = ''
        
    def get_t_access_token(self):
        # 获取 tenant token s
        url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
        params = { 'app_id': APP_ID, 'app_secret': APP_SECRET  } 

        ret = requests.post(url, params=params)
        print(f'-- get_t_access_token ret : {ret}\n {ret.text} ' ) 

        ret_dict = json.loads(ret.text)
        tenant_access_token = ret_dict.get('tenant_access_token', '')
        print(f'-- tenant_access_token : {tenant_access_token} ' ) 
        
        self.t_access_token = tenant_access_token  
        return tenant_access_token
    
        
    def get_wiki_list(self): 
        # 获取知识库列表
        request: ListSpaceRequest = ListSpaceRequest.builder() \
            .page_size(20) \
            .lang("en") \
            .build()
     
        option = lark.RequestOption.builder().tenant_access_token(self.t_access_token).build()   
        response: ListSpaceResponse = self.client.wiki.v2.space.list(request, option)  

        # 处理失败返回
        if not response.success():
            log_response_err(response) 
            return

        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
    
    
    # space_id 为数字, 如 ： 7472273664856096769 
    def get_wiki_space_info(self, space_id):  
        # 获取知识库空间信息 
        request: GetSpaceRequest = GetSpaceRequest.builder() \
            .space_id(space_id) \
            .lang("zh") \
            .build()

        option = lark.RequestOption.builder().tenant_access_token(self.t_access_token).build() 
        response: GetSpaceResponse = self.client.wiki.v2.space.get(request, option)
 
        if not response.success():
            log_response_err(response) 
            return

        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))



    #  wiki_token 为字符串，如 Rj5iwFfVTiv504krkEncrHnjnkg, 为知识库链接后缀  
    # 查询整个知识库，或知识库下节点的详细信息 
    def get_wiki_node_info(self, wiki_token): 
        # 获取知识库节点信息

        
        request: GetNodeSpaceRequest = GetNodeSpaceRequest.builder() \
            .token(wiki_token) \
            .obj_type("wiki") \
            .build()

        # 发起请求
        option = lark.RequestOption.builder().tenant_access_token(self.t_access_token).build() 
        response: GetNodeSpaceResponse = self.client.wiki.v2.space.get_node(request, option)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.wiki.v2.space.get_node failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return

        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4)) 
        '''
        {
        "node": {
            "space_id": "7472273664856096769",
            "node_token": "Rj5iwFfVTiv504krkEncrHnjnkg",
            "obj_token": "WNFrdiIdwoBFsAxV4wOcjzZmnfd",
            "obj_type": "docx",
            "parent_node_token": "",
            "node_type": "origin",
            "origin_node_token": "Rj5iwFfVTiv504krkEncrHnjnkg",
            "origin_space_id": "7472273664856096769",
            "has_child": true,
            "title": "English enhancement",
            "obj_create_time": "1739774287",
            "obj_edit_time": "1741171325",
            "node_create_time": "1739774287",
            "creator": "ou_3b6c7a8e6cd22bf0b8128c326ee389bf",
            "owner": "ou_3b6c7a8e6cd22bf0b8128c326ee389bf",
            "node_creator": "ou_3b6c7a8e6cd22bf0b8128c326ee389bf"
        }
    }
        '''


    # space_id 为整数，非字符串，如 7472273664856096769
    # 当一个节点的 has_child 为true 时，将这个节点的 node_token 传递为 parent_node_token  
    def get_wiki_sub_nodes(self, space_id, page_token='', parent_node_token=''):
        
        
        request: ListSpaceNodeRequest = ListSpaceNodeRequest.builder() \
            .space_id( space_id ) \
            .page_token(page_token) \
            .page_size(50) \
            .parent_node_token(parent_node_token) \
            .build()

        # 发起请求
        option = lark.RequestOption.builder().tenant_access_token(self.t_access_token).build() 
        response: ListSpaceNodeResponse = self.client.wiki.v2.space_node.list(request, option)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.wiki.v2.space_node.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return

        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return response.data 
        
        '''
    {
        "items": [
            {
                "space_id": "7472273664856096769",
                "node_token": "Rj5iwFfVTiv504krkEncrHnjnkg",
                "obj_token": "WNFrdiIdwoBFsAxV4wOcjzZmnfd",
                "obj_type": "docx",
                "parent_node_token": "",
                "node_type": "origin",
                "origin_node_token": "Rj5iwFfVTiv504krkEncrHnjnkg",
                "origin_space_id": "7472273664856096769",
                "has_child": true,
                "title": "English enhancement",
                "obj_create_time": "1739774287",
                "obj_edit_time": "1741171325",
                "node_create_time": "1739774287",
                "creator": "ou_3b6c7a8e6cd22bf0b8128c326ee389bf",
                "owner": "ou_3b6c7a8e6cd22bf0b8128c326ee389bf"
            },
            {
                "space_id": "7472273664856096769",
                "node_token": "XOO6w73wai2WPykVQCYclWHdn7f",
                "obj_token": "AiyAdSarmo17Slxk1c0c13vznEc",
                "obj_type": "docx",
                "parent_node_token": "",
                "node_type": "origin",
                "origin_node_token": "XOO6w73wai2WPykVQCYclWHdn7f",
                "origin_space_id": "7472273664856096769",
                "has_child": true,
                "title": "Technical enhancements ",
                "obj_create_time": "1739774287",
                "obj_edit_time": "1741171225",
                "node_create_time": "1739774287",
                "creator": "ou_3b6c7a8e6cd22bf0b8128c326ee389bf",
                "owner": "ou_3b6c7a8e6cd22bf0b8128c326ee389bf"
            },
            ...
            {
                "space_id": "7472273664856096769",
                "node_token": "PL1owykFEiZI68kx4MbcNHjgnDc",
                "obj_token": "ILe8smDT2htzratYbdvcddsMnqe",
                "obj_type": "sheet",
                "parent_node_token": "",
                "node_type": "origin",
                "origin_node_token": "PL1owykFEiZI68kx4MbcNHjgnDc",
                "origin_space_id": "7472273664856096769",
                "has_child": false,
                "title": "项目甘特图 Pro",
                "obj_create_time": "1741178155",
                "obj_edit_time": "1741178161",
                "node_create_time": "1741178155",
                "creator": "ou_3b6c7a8e6cd22bf0b8128c326ee389bf",
                "owner": "ou_3b6c7a8e6cd22bf0b8128c326ee389bf"
            }
        ],
        "page_token": "",
        "has_more": false
    }
        '''
    
        pass 


    def get_wiki_sub_nodes_all(self, space_id):

        all_items = []
        page_token = ''
        while 1:
            resp = self.get_wiki_sub_nodes(space_id, page_token) 
            all_items.extend(resp.items) 
            if resp.has_more == False:break
            page_token = resp.page_token 
            
            
        print(f'-- all_items : {len(all_items)} ' ) 
        return all_items 
    


    # 如 IAB7s6EfghCG5itfWDwcGzcFn9c
    # 一个 sheet 文件，可能包含多个 sheet 
    def get_sheet_id(self, obj_token):
        # 获取 sheet id 
        
        request: QuerySpreadsheetSheetRequest = QuerySpreadsheetSheetRequest.builder() \
            .spreadsheet_token(obj_token) \
            .build()

        # 发起请求
        option = lark.RequestOption.builder().tenant_access_token(self.t_access_token).build() 
        response: QuerySpreadsheetSheetResponse = self.client.sheets.v3.spreadsheet_sheet.query(request, option)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.sheets.v3.spreadsheet_sheet.query failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return

        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))  
        
        
        return response.data 
        
        # 0Hsxos 
        
    '''
    {
        "sheets": [
            {
                "sheet_id": "0Hsxos",
                "title": "项目管理",
                "index": 0,
                "hidden": false,
                "grid_properties": {
                    "frozen_row_count": 5,
                    "frozen_column_count": 0,
                    "row_count": 34,
                    "column_count": 65
                },
                "resource_type": "sheet",
                "merges": [
                    {
                        "start_row_index": 0,
                        "end_row_index": 0,
                        "start_column_index": 0,
                        "end_column_index": 8
                    },
                    ...
                    {
                        "start_row_index": 4,
                        "end_row_index": 4,
                        "start_column_index": 3,
                        "end_column_index": 7
                    }
                ]
            },
            {
                "sheet_id": "GkKBut",
                "title": "项目甘特图",
                "index": 1,
                "hidden": false,
                "resource_type": "bitable"
            },
            ...
            {
                "sheet_id": "omaSJw",
                "title": "节假日一览表",
                "index": 4,
                "hidden": false,
                "grid_properties": {
                    "frozen_row_count": 0,
                    "frozen_column_count": 0,
                    "row_count": 194,
                    "column_count": 20
                },
                "resource_type": "sheet",
                "merges": [
                    {
                        "start_row_index": 0,
                        "end_row_index": 1,
                        "start_column_index": 5,
                        "end_column_index": 7
                    },
                    ...
                    {
                        "start_row_index": 6,
                        "end_row_index": 7,
                        "start_column_index": 5,
                        "end_column_index": 7
                    }
                ]
            }
        ]
    }
    '''
    

    def create_export_task(self, obj_token, obj_type, sub_id=''):
        # 创建导出任务 
        print(f'-- create_export_task : {obj_token} ' ) 

        file_extension = obj_type
        if obj_type == 'sheet' or obj_type=='bitable':
            file_extension = 'xlsx'     
            
        
        
        request: CreateExportTaskRequest = CreateExportTaskRequest.builder() \
            .request_body(ExportTask.builder()
                .file_extension(file_extension)
                .token(obj_token)
                .type(obj_type)
                .sub_id(sub_id)
                .build()) \
            .build()

        # 发起请求
        option = lark.RequestOption.builder().tenant_access_token(self.t_access_token).build() 
        response: CreateExportTaskResponse = self.client.drive.v1.export_task.create(request, option)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.drive.v1.export_task.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return

        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        '''
        { "ticket": "7478302427408400403" }
        ''' 
        ticket = response.data.ticket 
        return ticket  

    def check_export_task(self, ticket, obj_token):
        # 检查导出任务 
        print(f'-- check_export_task : {ticket} {obj_token}' ) 
        
        request: GetExportTaskRequest = GetExportTaskRequest.builder() \
            .ticket(ticket) \
            .token(obj_token) \
            .build()

        # 发起请求
        option = lark.RequestOption.builder().tenant_access_token(self.t_access_token).build() 
        response: GetExportTaskResponse = self.client.drive.v1.export_task.get(request, option)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.drive.v1.export_task.get failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return

        # 处理业务结果
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        
        return response.data 
        
    '''
    {
    "result": {
        "file_extension": "docx",
        "type": "docx",
        "file_name": "English enhancement",
        "file_token": "HGZbbG4hAoa2QDxpRBXcPO43nrh",
        "file_size": 3664,
        "job_error_msg": "success",
        "job_status": 0
    }
    }
    ''' 

    # 下载 pdf 文件 
    def download_file(self, obj_token, save_dir): 
        # 下载 pdf 类型文件  
        request: DownloadFileRequest = DownloadFileRequest.builder() \
            .file_token(obj_token) \
            .build()

        # 发起请求
        option = lark.RequestOption.builder().tenant_access_token(self.t_access_token).build() 
        response: DownloadFileResponse = self.client.drive.v1.file.download(request, option)

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.drive.v1.file.download failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return

        if not os.path.isdir(save_dir):os.makedirs(save_dir) 
        file_name =  unquote(response.file_name).replace(' ', '_').replace('/', '_') 
        save_path = os.path.join(save_dir, file_name) 
        
        print('-- download_file : ', save_path)
        
        f = open(save_path, "wb")
        f.write(response.file.read())
        f.close()

    
    def export_file(self, file_token, save_dir):
        # 导出文件  
        print(f'-- export_file : {file_token} | {save_dir}' )   

        
        request: DownloadExportTaskRequest = DownloadExportTaskRequest.builder() \
            .file_token(file_token) \
            .build() 

        # 发起请求
        option = lark.RequestOption.builder().tenant_access_token(self.t_access_token).build() 

        response: DownloadExportTaskResponse = self.client.drive.v1.export_task.download(request, option)

        # 处理失败返回
        if not response.success():
            print(f'-- status_code : {response.raw.status_code} |  {response.raw.content} ' ) 
            
            lark.logger.error(
                f"client.drive.v1.export_task.download failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()} ")
            
            # lark.logger.error(
            #     f"client.drive.v1.export_task.download failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return
        
        
        if not os.path.isdir(save_dir):os.makedirs(save_dir) 
        file_name =  unquote(response.file_name).replace(' ', '_').replace('/', '_') 
        save_path = os.path.join(save_dir, file_name) 
        #
        print('-- export_file : ', save_path)
        f = open(save_path, "wb")
        f.write(response.file.read())
        f.close()  

if __name__ == "__main__":
    
    pass 
               
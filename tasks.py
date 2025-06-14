import os 
import time  
from config import *
from feishu_admin import FeishuAdmin

# 文件保存根目录
save_root_dir = 'feishu-doc'  


admin = FeishuAdmin()  


def export_file_obj(obj_token, obj_type, save_dir=save_root_dir): 
    # 导出文件对象 
    # print(f'-- export_file : {obj_token} {obj_type} ' )  
    
    if obj_type != 'sheet' and obj_type != 'bitable':
        return export_sub_file(obj_token, obj_type, save_dir=save_dir)
        
    sheets = admin.get_sheet_id(obj_token).sheets 
    print('-- sheets : ', len(sheets))
    for sheet in sheets: 
        export_sub_file(obj_token, obj_type, sub_id=sheet.sheet_id, save_dir=save_dir)   
    
        
def export_sub_file(obj_token, obj_type, sub_id='', save_dir=save_root_dir):
    # 导出子文件   
    ticket = admin.create_export_task(obj_token, obj_type, sub_id=sub_id)
    if ticket == None:
        print(f'xx create_export_task faild : {obj_token} {obj_type} {sub_id} ' ) 
        return
    
    time.sleep(2) 
    check_resp = admin.check_export_task(ticket, obj_token)
    if check_resp == None:
        time.sleep(2)
        
    file_token = check_resp.result.file_token
    admin.export_file(file_token, save_dir)
    

def prcs_item(item, space_id, page_token, save_dir=save_root_dir):
    
    title = item.title 
    print('\n\n---- ', title) 
    
    obj_type = item.obj_type
    obj_token = item.obj_token
     
    try: 
        if title.lower().endswith('.pdf'):
            admin.download_file(obj_token, save_dir)
        else:
            export_file_obj(obj_token, obj_type, save_dir=save_dir) 
    except Exception as err:
        print(f'xx export err : {err} ' ) 
    
    if item.has_child == False:return
    
    node_token = item.node_token 
    resp = admin.get_wiki_sub_nodes(space_id, page_token, parent_node_token=node_token)  
    
    save_dir = os.path.join(save_dir, title.replace(' ', '_').replace('/','_')) 
    
    for item in resp.items:
        prcs_item(item, space_id, page_token, save_dir) 
             
       

def export_wiki_documents():
    # 导出知识库所有文件
    admin.get_t_access_token() 
    # 查看有哪些知识库，以及对应的 space id 各是多少 
    admin.get_wiki_list() 
    # return  
    
    space_id = '7472273664856096769' 
    page_token = '' 
    while 1:
        resp = admin.get_wiki_sub_nodes(space_id, page_token)  
        if resp == None:break 
        
        for item in resp.items:
            prcs_item(item, space_id, page_token) 
              
        if resp.has_more == False:break
        page_token = resp.page_token 
        
    


if __name__ == '__main__':
    
    export_wiki_documents()


from celery import Celery
from enum import Enum
from dotenv import dotenv_values
import json
import re 
import pprint as pp
from sqlalchemy.orm import sessionmaker
import _Modules._sqlalchemy.sqlalchemycontrol as SQLControl
import _Classes._unique.TableDefs as Table
from OT6_API.OT6API_DEVICE import DEVICE as APIClient
from datetime import datetime

def Verify_Data(EITMSValue,Current_DB_EITMS):
    Update = ""
    if EITMSValue in Current_DB_EITMS:
        Update = 'Update'
    elif EITMSValue not in Current_DB_EITMS:
        Update = 'Insert'
    if Update == "":
        Update = 'Resolved'
    return Update

def Parse_Data_from_OT6(Automation,Current_DB_EITMS):
        for device in Automation['results_keys']:
                    
            Results=Ot6Client.automation_config(device).json()
            Name = Results['data_title']
            Tabs_info = Results['tab_info']
            Tabs = Results['tabs']
            Name_Eitms = Name.replace("/", " ")

            json_file=open("./Output/Automation/Automation_"+str(aisle)+"_"+Name_Eitms.strip()+".txt", mode="w")
            json_file.write(json.dumps(Results, indent=3))
            json_file.close()

            InventoryTab = 0
            AutomationTab = 0
            
            for key in Tabs_info.keys():
                match Tabs_info[key][1]:
                    case 'Inventory Details':
                        InventoryTab = key
                    case 'Automation Config':
                        AutomationTab = key
            
            AutoData = {}
            InvenData= {}
            AutoData['Automation'] = True
            InvenData['data_title'] = Results['data_title']
            
            if InventoryTab != 0:
                range = int(len(Tabs[InventoryTab]['data']))
                x=0
                while x <= (range-1):
                    for tag in Tabs[InventoryTab]['data'][x]:
                        InvenData[tag[0]]= tag[1]
                    x=x+1
            if AutomationTab != 0:
                range = int(len(Tabs[AutomationTab]['data']))
                x=0
                while x <= (range-1):
                    for tag in Tabs[AutomationTab]['data'][x]:
                        AutoData[tag[0]]= tag[1]
                    x=x+1 
            else:
                AutoData['Automation'] = False
            
            UpdateType = Verify_Data(InvenData['EITMS Tag Code'],Current_DB_EITMS)
            InsertData = Map_OT6_toDB(InvenData,AutoData)
            match UpdateType:
                case "Update":
                    pass
                case "Insert":
                    InsertData['time_created'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    SQLControl.dbInsertData(config['DBCONNECT'],Table.Device, InsertData)
                case "Resolved":
                    pass
    

def Merge(dict1, dict2):
    return(dict1.update(dict2))

def Map_OT6_toDB(InvenData, AutoData):
    MappedData = {}
    Merge(InvenData,AutoData)
    Aisle = InvenData['Aisle / Rack'].split()[1]
    Rack = InvenData['Aisle / Rack'].split()[4]
    MappedData['data_title'] = InvenData['data_title']
    MappedData['device_type'] = InvenData['Device Type']
    MappedData['lab'] = InvenData['Lab']
    MappedData['aisle'] = Aisle
    MappedData['rack'] = Rack
    MappedData['model_number'] = InvenData['Model Number']
    MappedData['serial_number'] = InvenData['Serial Number']
    MappedData['manufacturer'] = InvenData['Manufacturer']
    MappedData['eitms'] = InvenData['EITMS Tag Code']
    MappedData['sync_time'] = InvenData['EITMS Sync']
    MappedData['automation_yes_no'] = InvenData['Automation']
    if InvenData['Automation'] != False:
        MappedData['power_status'] = InvenData['Power Status']
        MappedData['power_policy'] = InvenData['Power Policy']
    MappedData['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return MappedData

config = dotenv_values()
SQLControl.dbDatabaseDrop(config['DBCONNECT'])
SQLControl.dbDatabaseCreate(config['DBCONNECT'])
SQLControl.dbTableCreate(config['DBCONNECT'])


class Site(Enum):
    RCDN = "6_1"
    RTP = "1_1"
    ESCALATION = "7_1"
    Unknown = "Unknown"

    @staticmethod
    def from_str(name: str) -> "Site":
        try:
            return Site(name)
        except ValueError:
            try:
                return Site[name]
            except KeyError:
                return Site.Unknown

Ot6Client = APIClient(config['OT6_API_KEY'])

# Search = Ot6Client.device_search_aka()
# Search[Ot6Client.MenuItem['group']]='272_1'
# Response = Ot6Client.search_devices(Search).json()
# json_file=open("./Output/Json/ff10.txt", mode="w")
# json_file.write(json.dumps(Response['records'], indent=3))
# json_file.close()

for aisle in Ot6Client.F340_Lab_Aisle:
    Params = {}
    Params['aisle_rack'] = Ot6Client.F340_Lab_Aisle.get(aisle)
    Automation=Ot6Client.view_lab_audit_power('RTPF12340TSGeneral',Params).json()
    json_Automation=open("./Output/Lab_Audit/Lab_Audit_Power_"+'RTPF12340TSGeneral_Lab_Audit_'+str(aisle)+".txt", mode="w")
    json_Automation.write(json.dumps(Automation, indent=3))
    json_Automation.close()

    # code to be implemented later for entire lab search 
    # Eitms=Ot6Client.view_lab_audit_eitms('RTPF12340TSGeneral',Params).json()
    # json_Eitms=open("./Output/Lab_Audit/Lab_Audit_Eitms_"+'RTPF12340TSGeneral_Lab_Audit_'+str(aisle)+".txt", mode="w")
    # json_Eitms.write(json.dumps(Eitms, indent=3))
    # json_Eitms.close()
#    try:

    #dbSelectData(connection_string,TableorFields,WhereClause="",Orderby=""):
    Current_DB_EITMS = SQLControl.dbSelectData(config['DBCONNECT'],Table.Device, 'eitms')
    Dataset = Parse_Data_from_OT6(Automation,Current_DB_EITMS)
    

            # json_file.write(Results['tab_info'])
            # json_file.write('\n')
            # json_file.write(Results['tabs'])
            # json_file.write('\n}')
            # 
#    except:
#        pass
    
# XR_chassis = []
# for record in Response['records'].keys():
#     Chassis = ""
#     FilenameXR = "./Output/Chassis/"
#     FilenameOdd = "./Output/Odd/"
#     if len(Response['records'][record]) > 0:
#         StandAloneXR =re.search('Standalone', json.dumps(Response['records'][record]['group_name_plain']))
#         SharedXR =re.search('Shared', json.dumps(Response['records'][record]['group_name_plain']))
#         ChassisCRS = re.search('CRS', json.dumps(Response['records'][record]['group_name_plain']))
#         if StandAloneXR or SharedXR:
#             Match8000 = re.search('^"8', json.dumps(Response['records'][record]['aka_name']))
#             if Match8000:
#                 Chassis = Match8000.string.strip('"')
#                 Chassis = Chassis.strip(" ")
#                 filename = FilenameXR+Chassis+".txt"
#             Match12000 = re.search('^"12', json.dumps(Response['records'][record]['aka_name']))
#             if Match12000:
#                 Chassis = Match12000.string.strip('"')
#                 Chassis = Chassis.strip(" ")
#                 filename = FilenameXR+Chassis+".txt"
#             MatchASR = re.search('^"ASR-', json.dumps(Response['records'][record]['aka_name']))
#             if MatchASR:
#                 Chassis = MatchASR.string.strip('"')
#                 Chassis = Chassis.strip(" ")
#                 filename = FilenameXR+Chassis+".txt"
#             MatchCRS = re.search('^"CRS-', json.dumps(Response['records'][record]['aka_name']))
#             if MatchCRS:
#                 Chassis = MatchCRS.string.strip('"')
#                 Chassis = Chassis.strip(" ")
#                 filename = FilenameXR+Chassis+".txt"
#             MatchNCS = re.search('^"NCS-', json.dumps(Response['records'][record]['aka_name']))
#             if MatchNCS:
#                 Chassis = MatchNCS.string.strip('"')
#                 Chassis = Chassis.strip(" ")
#                 filename = FilenameXR+Chassis+".txt"
#             MatchWBD = re.search('^"WBD-', json.dumps(Response['records'][record]['aka_name']))
#             if MatchWBD:
#                 Chassis = MatchWBD.string.strip('"')
#                 Chassis = Chassis.strip(" ")
#                 filename = FilenameXR+Chassis+".txt"
#         if ChassisCRS:
#             Chassis = json.dumps(Response['records'][record]['aka_name'])
#             if Chassis == '""' or Chassis == "null":
#                 Chassis = json.dumps(Response['records'][record]['eitms_tag_code'])
#             Chassis = Chassis.strip('"')
#             Chassis = Chassis.strip(" ")
#             filename = FilenameOdd+Chassis+".txt"


#         if StandAloneXR or ChassisCRS or SharedXR:
#             chassis_file=open(filename, mode="w")
#             chassis_file.write(json.dumps(Response['records'][record], indent=3))
#             chassis_file.flush()
#             chassis_file.close()


# @app.task
# def fetch_xr_device():
#     pass

# def get_xr_devices(client: Ot6Client, site: Site):
#     args = {
#         "menu_36_1": "equipment_chassis",  # device type: equipment
#         "menu_35_1": site.value,
#     }

#     if site is Site.RTP:
#         args["menu_38_1"] = "111_1"  # lab: RTP F12-340 (TS General)
#         args["menu_39_1"] = ""  # group: IOS-XR: All
#     elif site is Site.RCDN:
#         args["menu_38_1"] = "151_1"  # lab: RCDN 51-3E (TS General)
#         args["menu_39_1"] = "2077_2"  # group: IOS-XR: All
#     else:
#         return []

#     devices = client.search_checkout(args=args)

#     args["menu_36_1"] = "Virtual Machine"  # device type
#     devices += client.search_checkout(args=args)

#     return [d for d in devices if "Shared" in d.group or "Standalone" in d.group]
# # result = add.delay(4,4)
# # while True:
    
# #     print(app.backend.get_result(result.id))
# #     print(result.status)
# #     print(result.result)

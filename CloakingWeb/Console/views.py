from django.shortcuts import render
from CloakingWeb.settings import MONGO, DEBUG, SHORT_LINKS
from pymongo import MongoClient
from django.http import JsonResponse
import json
from pymongo import MongoClient
from pprint import pprint

# Create your views here.
def switch(request):
    if request.method not in ["GET", "POST"]:
        return JsonResponse({}, status = 405)
    
    if request.method == "GET":
        client = MongoClient(MONGO)
    
        result = client['Test_Console' if DEBUG else 'Console']['in_switch'].find_one(
            filter={}
        )
        
        open = False # True can access ab, False only a
        showb = False
        if result:
            try:
                open = result['open']
            except:
                pass
            
            try:
                showb = result['showb']
            except:
                pass
        
        return render(request, 'console/switch.html', context={"open":open, "showb":showb})
    
    # POST
    data = {}
    try:
        open = json.loads(request.body)['open']
        print("open", open)
        data = {
            "open":open
        }
    except:
        try:
            showb = json.loads(request.body)['showb']
            print("showb", showb)
            data = {
                "showb":showb
            }
        except Exception as e:
            print(e)
            return JsonResponse({'status':'No change.'})
    
    try:
        client = MongoClient(MONGO)
    
        result = client['Test_Console' if DEBUG else 'Console']['in_switch'].find_one(
            filter={}
        )
        
        if result:
            print(result)
            _ = client['Test_Console' if DEBUG else 'Console']['in_switch'].update_one(
                filter={
                    "_id":result["_id"]
                },
                update={
                    "$set":data
                }
            )
            print(_.matched_count)
        else:
            client['Test_Console' if DEBUG else 'Console']['in_switch'].insert_one(
                data
            )
        
        return JsonResponse({'status':'OK.'})
    except Exception as e:
        print(e)
        return JsonResponse({'status':'No change.'})
    
def report(request):   
    if request.method not in ["GET"]:
        return JsonResponse({}, status=405)
    
    
    if request.headers['Accept'] != "application/json":
        return render(request, 'console/report.html')
 

    try:
        start_ts = int(request.GET["start_ts"])
        end_ts = int(request.GET["end_ts"])
        print(start_ts, end_ts)
    except Exception as e:
        print("param error", e)
        return JsonResponse({"status": "Parameter Error."}, status=400)

    try:
        res = get_log(start_ts, end_ts)
        # print(res)
    except Exception as e:
        raise       

    return JsonResponse(res, safe=False)
        
    
        
def get_log(start_ts, end_ts): 
    
    def getAccessData(start_ts, end_ts):
        client = MongoClient(MONGO)
        filter = {
            "time": {
                "$gte": start_ts,
                "$lt": end_ts,
            },
            'ABPage': 'B',
            'PageName': 'index'
        }
        project = {
            'Referer': 1,
            'gclid': 1,
            'state': 1,
            'time': 1
        }

        result = client['ABPage']['in_access'].find(
            filter=filter,
            projection=project,
        )

        return tuple(result)

    def getLinkData(start_ts, end_ts):
        client = MongoClient(MONGO)
        filter = {
            "time": {
                "$gte": start_ts,
                "$lt": end_ts,
            },
            'ABPage': 'B',
            'PageName':{"$in":list(SHORT_LINKS.keys())},
        }
        project = {
            'Referer': 1,
            'gclid': 1,
            'state': 1,
            'time': 1
        }

        result = client['ABPage']['in_access'].find(
            filter=filter,
            projection=project,
        )

        return tuple(result)
    
    def trans(r):
        try:
            if r == "--":
                return r
            return f"{r*100:.2f}%"
        except Exception as e:
            print("trans error.", e)
            return None

    def summary(detail, linkData):
        click = []
        view = []
        for res in detail:
            view.append(res['gclid'])

            try:
                if 'google' not in res['Referer']:
                    continue
            except:
                continue

            click.append(res['gclid'])

        google_click_no_repeat = len(set(click))
        google_click_total = len(click)

        B_index_view_no_repeat = len(set(view))
        B_index_view_total = len(view)

        link_click = len(linkData)
        link_click_no_repeat = len(set([ld['state'] for ld in linkData]))

        return [
            google_click_no_repeat, 
            google_click_total, 
            B_index_view_no_repeat, 
            B_index_view_total,
            trans(google_click_no_repeat/google_click_total) if google_click_total != 0 else "--",
            trans(B_index_view_no_repeat/B_index_view_total) if B_index_view_total != 0 else "--",
            trans(google_click_no_repeat/B_index_view_no_repeat) if B_index_view_no_repeat != 0 else "--",
            trans(google_click_total/B_index_view_total) if B_index_view_total != 0 else "--",
            link_click_no_repeat,
            link_click,
            trans(link_click_no_repeat/google_click_no_repeat) if google_click_total != 0 else "--",
        ]
          
    def daliyCut(result, start_ts, end_ts, linkData_A):
        datas = {}
        datas_link = {}
        end = end_ts
        day_sec = 24*60*60
        while end > start_ts:
            datas[(end - day_sec, end)] = []
            datas_link[(end - day_sec, end)] = []
            
            end -= day_sec
        
        for res in result:
            for daily_range in datas.keys():
                if res['time'] >= daily_range[0] and res['time'] < daily_range[1]:
                    datas[daily_range].append(res)
                    break
        
        for res in linkData_A:
            for daily_range in datas_link.keys():
                if res['time'] >= daily_range[0] and res['time'] < daily_range[1]:
                    datas_link[daily_range].append(res)
                    break
        
        return datas, datas_link
        
    def toMatrix(summary_list):
        return [
            [summary_list[0], summary_list[1], summary_list[4]],
            [summary_list[2], summary_list[3], summary_list[5]],
            [summary_list[6], summary_list[7], None],
        ]
    
    def calcRatio(input_list):
        for i in range(len(input_list[0])):
            if i >= 4 and i !=8 and i != 9:
                input_list[2].append(None)
                continue
            
            after = input_list[0][i]
            before = input_list[1][i]
            
            print(after, before)
            
            calc_res = trans((after-before)/before if before != 0 else "--")
            
            input_list[2].append(calc_res)
        
    def transMaxtrix(ori_list):
        new_row = len(ori_list[0])
        new_col = len(ori_list)

        new_list = []

        for nr in range(new_row):
            new_list.append([])
            for nc in range(new_col):
                new_list[nr].append(ori_list[nc][nr])

        return new_list


    detail_A = getAccessData(start_ts, end_ts)
    linkData_A = getLinkData(start_ts, end_ts)
    summary_A = summary(detail_A, linkData_A)
    output1 = toMatrix(summary_A)

    gap_ts = end_ts - start_ts
    detail_B = getAccessData(start_ts - gap_ts, end_ts - gap_ts)
    linkData_B = getLinkData(start_ts - gap_ts, end_ts - gap_ts)
    summary_B = summary(detail_B, linkData_B)
    output2 = [
        summary_A,
        summary_B,
        []
    ]
    calcRatio(output2)
    output2 = transMaxtrix(output2)

    detail_daily, link_daily = daliyCut(detail_A, start_ts, end_ts, linkData_A)
    
    output3 = []
    for date_range, daily_data in detail_daily.items():
        print(date_range)
        
        output3.append(summary(daily_data, link_daily[date_range]))
    output3 = transMaxtrix(output3)


    # pprint(output3)

    data = [output1, output2, output3]
    # pprint(data)

    return data
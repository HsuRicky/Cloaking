from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
import json
from CloakingWeb.settings import MONGO, GOOGLE_AGENT_KWD, ALLOWED_COUNTRY, ALLOWED_REFERRER, DEBUG, SHORT_LINKS
from pymongo import MongoClient
import time
import hashlib
import os

# Create your views here.
def abChoose(headers, state, PageName, gclid):
    # return "A"
    
    UA = ""
    try:
        UA = headers["User-Agent"]
    except Exception as e:
        print("User-Agent Error", e)
    print("UA", UA)
    
    CfIpcountry = ""
    try:
        CfIpcountry = headers["Cf-Ipcountry"]
    except Exception as e:
        print("Cf-Ipcountry Error", e)
    print("CfIpcountry", CfIpcountry)
    
    Referer = ""
    try:
        Referer = headers["Referer"]
    except Exception as e:
        print("Referer Error", e)
        
    print("Referer", Referer)
    
    client = MongoClient(MONGO)
    
    switch = False
    showb = False
    try:
        _ = client['Test_Console' if DEBUG else 'Console']['in_switch'].find_one(
                filter={}
            )
        print("switch mongo", _)
        
        try:
            switch = _['open']
            print("switch", switch)
        except Exception as e:
            print("switch fail", e)
            pass
            
        try:
            showb = _['showb']
            print("showb", showb)
        except Exception as e:
            print("showb fail", e)
            pass
    except:
        pass
    
    result = None
    if showb:
        print("showb")
        result = "B"
    else:
        if not switch:
            print("switch not open")
            result = "A"
        else:
            if sum([1 if UA in kwd else 0 for kwd in GOOGLE_AGENT_KWD]) != 0:
                print("User-Agent is google")
                result = "A"
            else:
                if sum([1 if al_ref in Referer else 0 for al_ref in ALLOWED_REFERRER]) != 0 and CfIpcountry == ALLOWED_COUNTRY:
                    print("from (google or self) and IN")
                    result = "B"
                else:
                    print("not (from google and IN)")
                    result = "A"
    
    data = {k:v for k, v in headers.items()}
    data["time"] = time.time()
    data["ABPage"] = result
    data["PageName"] = PageName
    data["state"] = state
    data["gclid"] = gclid

    client['Test_ABPage' if DEBUG else 'ABPage']['in_access'].insert_one(data)
    
    return result

def index(request):
    try:
        if request.session['state']:
            state = request.session['state']
        else:
            raise
    except:
        state = hashlib.sha256(os.urandom(1024)).hexdigest()
        request.session['state'] = state
    
    if request.method != "GET":
        return JsonResponse({}, status=405)
    
    gclid = request.GET.get('gclid')
    
    ABPage = abChoose(request.headers, state, "index", gclid)
    if ABPage == "A":
        return render(request, 'abpage/a.html')
    elif ABPage == "B":
        return render(request, 'abpage/b.html')

    
def cuttly(request, no):
    try:
        if request.session['state']:
            state = request.session['state']
        else:
            raise
    except:
        state = hashlib.sha256(os.urandom(1024)).hexdigest()
        request.session['state'] = state

    if request.method != "GET":
        return JsonResponse({}, status=405)
    
    gclid = request.GET.get('gclid')

    # record
    ABPage = abChoose(request.headers, state, no, gclid)
    
    # 重新導向
    if no in SHORT_LINKS and ABPage == "B":
        return redirect(SHORT_LINKS[no])
    else:
        return HttpResponseRedirect('/')
    
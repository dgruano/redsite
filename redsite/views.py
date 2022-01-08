from django.shortcuts import render
from django.http import HttpResponse
import redcharge.redcharge as red
from django.views.decorators.csrf import csrf_protect

from datetime import datetime, timedelta
import pytz
import pandas as pd

@csrf_protect
def redsite(request):
    if request.method == 'GET':
        d1, d2 = red.get_todays_date()

        # Format datetimes
        d1 = d1.strftime("%Y-%m-%dT%H:%M")
        d2 = d2.strftime("%Y-%m-%dT%H:%M")

        context = {'d1': d1, 'd2': d2}
        return render(request, 'index.html', context)

@csrf_protect
def result(request):
    if request.method == 'POST':
        # Parse request data
        start_date = datetime.strptime(request.POST['start_date'], "%Y-%m-%d")
        end_date = datetime.strptime(request.POST['end_date'], "%Y-%m-%d").replace(hour=23, minute=59)
        charge_hours = int(request.POST['charge_hours'])

        start_date_str = start_date.strftime("%Y-%m-%dT%H:%M")
        end_date_str = end_date.strftime("%Y-%m-%dT%H:%M")

        # Get the data
        data = red.get_price_data(start_date, end_date)

        # Optimize charging schedule
        opt = red.optimize_charge_pd(data, charge_hours)

        # Localize result data
        tz = pytz.timezone('Europe/Madrid')
        opt["time"] = opt["time"].dt.tz_localize(pytz.utc).dt.tz_convert(tz)
        opt["hour"] = pd.to_datetime(opt["time"]).dt.hour

        opt_start = opt["time"][0]
        opt_end = opt["time"][0] + timedelta(hours=charge_hours)
        avg_price = round(opt["average"][0], 1)
        
        context = {
            "start_date": start_date,
            "end_date": end_date,
            "charge_hours": charge_hours,
            "opt_start": opt_start,
            "opt_end": opt_end,
            "avg_price": avg_price,
        }
        return render(request, 'result.html', context)

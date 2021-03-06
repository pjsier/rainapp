import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render

from csos.models import RiverCso, RiverOutfall
from events.analyzer import rainfall_graph, find_n_years, build_flooding_data
from events.models import HourlyPrecip, NYearEvent
from flooding.models import BasementFloodingEvent


def index(request):
    _default_start = '07/22/2011 08:00'
    _default_end = '07/23/2011 06:00'
    return show_date(request, _default_start, _default_end)


def show_date(request, start_stamp, end_stamp):
    ret_val = {}

    try:
        start = pd.to_datetime(start_stamp)
        end = pd.to_datetime(end_stamp)

        ret_val['start_date'] = start.strftime("%m/%d/%Y %H:%M")
        ret_val['end_date'] = end.strftime("%m/%d/%Y %H:%M")

        hourly_precip_dict = list(
            HourlyPrecip.objects.filter(
                start_time__gte=start,
                end_time__lte=end
            ).values()
        )
        hourly_precip_df = pd.DataFrame(hourly_precip_dict)

        ret_val['total_rainfall'] = "%s inches" % hourly_precip_df['precip'].sum()

        high_intensity = find_n_years(hourly_precip_df)
        if high_intensity is None:
            ret_val['high_intensity'] = 'No'
        else:
            ret_val['high_intensity'] = "%s inches in %s hours!<br>  A %s-year storm" % (
                high_intensity['inches'], high_intensity['duration_hrs'], high_intensity['n'])

        graph_data = {'total_rainfall_data': rainfall_graph(hourly_precip_df)}

        csos_db = RiverCso.objects.filter(open_time__range=(start, end)).values() | RiverCso.objects.filter(
            close_time__range=(start, end)).values()

        csos_df = pd.DataFrame(list(csos_db))

        csos = []
        ret_val['sewage_river'] = 'None'

        if len(csos_df) > 0:

            csos_df['duration'] = (csos_df['close_time'] - csos_df['open_time'])
            ret_val['sewage_river'] = "%s minutes" % int(csos_df['duration'].sum().seconds / 60)

            river_outfall_ids = csos_df['river_outfall_id'].unique()
            river_outfall_ids = list(river_outfall_ids)
            river_outfalls = RiverOutfall.objects.filter(
                id__in=river_outfall_ids,
                lat__isnull=False
            )

            for river_outfall in river_outfalls:
                csos.append({'lat': river_outfall.lat, 'lon': river_outfall.lon})

        cso_map = {'cso_points': csos}
        graph_data['cso_map'] = cso_map

        flooding_df = pd.DataFrame(
            list(BasementFloodingEvent.objects.filter(date__gte=start).filter(date__lte=end).values()))

        if len(flooding_df) > 0:
            graph_data['flooding_data'] = build_flooding_data(flooding_df)
            ret_val['basement_flooding'] = flooding_df[flooding_df['unit_type'] == 'ward']['count'].sum()
        else:
            graph_data['flooding_data'] = {}
            ret_val['basement_flooding'] = 0
        ret_val['graph_data'] = graph_data

    except ValueError as e:
        return HttpResponse("Not valid dates")

    ret_val['hourly_precip'] = str(hourly_precip_df.head())
    return render(request, 'show_event.html', ret_val)


def nyear(request, recurrence):
    recurrence = int(recurrence)
    ret_val = {'recurrence': recurrence, 'likelihood': str(int(1 / int(recurrence) * 100)) + '%'}

    events = []
    events_db = NYearEvent.objects.filter(n=recurrence)
    for event in events_db:
        date_formatted = event.start_time.strftime("%m/%d/%Y") + "-" + event.end_time.strftime("%m/%d/%Y")
        duration = str(event.duration_hours) + ' hours' if event.duration_hours <= 24 else str(
            int(event.duration_hours / 24)) + ' days'
        events.append({'date_formatted': date_formatted, 'inches': "%.2f" % event.inches,
                       'duration_formatted': duration,
                       'event_url': '/date/%s/%s' % (event.start_time, event.end_time)})
    ret_val['events'] = events
    ret_val['num_occurrences'] = len(events)

    return render(request, 'nyear.html', ret_val)

def viz_animation(request):
    return render(request, 'viz.html')

def basement_flooding(request):
    return render(request, 'flooding.html')

def viz_splash(request):
    return render(request, 'viz-splash.html')

def about(request):
    return render(request, 'about.html')

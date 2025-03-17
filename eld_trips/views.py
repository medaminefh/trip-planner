# eld_trips/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .forms import TripForm
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt
import os
from django.conf import settings
from math import ceil

def calculate_route(current, pickup, dropoff):
    geolocator = Nominatim(user_agent="trip_planner")
    try:
        curr_loc = geolocator.geocode(current)
        if not curr_loc: return {'error': f"Could not geocode current location: {current}"}
        pick_loc = geolocator.geocode(pickup)
        if not pick_loc: return {'error': f"Could not geocode pickup location: {pickup}"}
        drop_loc = geolocator.geocode(dropoff)
        if not drop_loc: return {'error': f"Could not geocode dropoff location: {dropoff}"}
        
        distance_to_pickup = geodesic((curr_loc.latitude, curr_loc.longitude), (pick_loc.latitude, pick_loc.longitude)).miles
        distance_to_dropoff = geodesic((pick_loc.latitude, pick_loc.longitude), (drop_loc.latitude, drop_loc.longitude)).miles
        total_distance = distance_to_pickup + distance_to_dropoff
        driving_time = (total_distance / 50) + 2
        fuel_stops = max(0, ceil(total_distance / 1000) - 1)
        total_time = driving_time + (fuel_stops * 0.5)
        
        coordinates = [
            [curr_loc.latitude, curr_loc.longitude],
            [pick_loc.latitude, pick_loc.longitude],
            [drop_loc.latitude, drop_loc.longitude]
        ]
        
        return {
            'instructions': [
                f"Start at {current}",
                f"Drive {distance_to_pickup:.1f} miles to {pickup} ({distance_to_pickup/50:.1f} hrs)",
                "Pick up load (1 hr)",
                f"Drive {distance_to_dropoff:.1f} miles to {dropoff} ({distance_to_dropoff/50:.1f} hrs)",
                "Drop off load (1 hr)"
            ] + ([f"Fuel stop (0.5 hr)"] * fuel_stops),
            'total_time': total_time,
            'total_distance': total_distance,
            'coordinates': coordinates
        }
    except Exception as e:
        return {'error': f"Geocoding error: {str(e)}"}

def generate_eld_log(trip_id, total_time, cycle_used, total_distance):
    logs = []
    remaining_time = total_time
    remaining_distance = total_distance
    day = 1
    
    while remaining_time > 0:
        daily_drive_time = min(11, remaining_time - 2 if day == 1 else remaining_time)
        daily_time = daily_drive_time + (2 if day == 1 else 0)
        daily_distance = (daily_drive_time / total_time) * total_distance if total_time > 0 else 0
        
        plt.figure(figsize=(10, 4))  # Line 61 where the warning occurs
        times = [0]
        statuses = ['Off Duty']
        
        if day == 1:
            times.extend([cycle_used, cycle_used + 1, cycle_used + 1 + daily_drive_time])
            statuses.extend(['Driving', 'On Duty', 'Driving'])
            if daily_time > daily_drive_time:
                times.append(cycle_used + daily_time)
                statuses.append('Off Duty')
        else:
            times.extend([0, daily_drive_time])
            statuses.extend(['Driving', 'Off Duty'])
        
        plt.step(times, range(len(statuses)), where='post')
        plt.yticks(range(len(statuses)), statuses)
        plt.xlabel('Hours')
        plt.title(f'ELD Log - Day {day}')
        
        media_dir = os.path.join(settings.MEDIA_ROOT, 'eld_logs')
        os.makedirs(media_dir, exist_ok=True)
        log_path = os.path.join(media_dir, f'eld_log_{trip_id}_day_{day}.png')
        plt.savefig(log_path)
        plt.close()  # Close the figure to free memory
        
        logs.append({
            'day': day,
            'image': f'/media/eld_logs/eld_log_{trip_id}_day_{day}.png',
            'distance': daily_distance,
            'drive_time': daily_drive_time,
            'total_time': daily_time
        })
        
        remaining_time -= daily_time
        remaining_distance -= daily_distance
        day += 1
    
    return logs

@api_view(['POST'])
def trip_api(request):
    form = TripForm(request.data)
    if form.is_valid():
        trip = form.save()
        route_data = calculate_route(
            trip.current_location,
            trip.pickup_location,
            trip.dropoff_location
        )
        
        if 'error' not in route_data:
            total_time = route_data['total_time']
            remaining_hours = 70 - trip.cycle_used
            compliance = "Warning: Trip exceeds 70-hr cycle limit" if total_time > remaining_hours else "Trip is within HOS limits"
            eld_logs = generate_eld_log(trip.id, total_time, trip.cycle_used, route_data['total_distance'])
            
            return Response({
                'route_instructions': route_data['instructions'],
                'total_distance': route_data['total_distance'],
                'total_time': route_data['total_time'],
                'compliance': compliance,
                'eld_logs': eld_logs,
                'coordinates': route_data['coordinates']
            })
        return Response({'error': route_data['error']}, status=400)
    return Response(form.errors, status=400)
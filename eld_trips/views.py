from rest_framework.decorators import api_view
from rest_framework.response import Response
from .forms import TripForm
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.shapes import Drawing, Line, String
from reportlab.lib.units import inch
import os
from django.conf import settings
from math import ceil
import matplotlib.pyplot as plt
from django.conf import settings


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

def generate_daily_log(trip_id, total_time, cycle_used, total_distance):
    logs = []
    remaining_time = total_time
    remaining_distance = total_distance
    day = 1

    while remaining_time > 0:
        daily_drive_time = min(11, remaining_time - 2 if day == 1 else remaining_time)
        daily_time = daily_drive_time + (2 if day == 1 else 0)  # Include pickup/dropoff on day 1
        daily_distance = (daily_drive_time / total_time) * total_distance if total_time > 0 else 0

        # Create PDF
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'daily_logs', f'daily_log_{trip_id}_day_{day}.pdf')
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'daily_logs'), exist_ok=True)

        doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=0.25*inch, rightMargin=0.25*inch, topMargin=0.25*inch, bottomMargin=0.25*inch)
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        normal = styles['Normal']
        normal.fontSize = 7  # Slightly larger for readability, matching typical log sheets
        heading = styles['Heading1']
        heading.fontSize = 10

        # Header
        header_data = [
            ["Driver's Daily Log", "", "", "", "", "Original: File at home terminal", "", "Duplicate: Driver retains in his/her possession for 8 days"],
            ["From:", "Chicago, IL", "To:", "Madison, WI", "Date:", f"March {16 + day}, 2025", "Year:", "2025"],
        ]
        header_table = Table(header_data, colWidths=[1.5*inch, 1*inch, 0.5*inch, 1*inch, 0.5*inch, 1.5*inch, 0.5*inch, 1.5*inch])
        header_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('SPAN', (0, 0), (4, 0)),  # Span "Driver's Daily Log" across first row
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.1*inch))

        # Top Section
        top_data = [
            ["Total Miles Driving Today", f"{daily_distance:.1f}", "", "Total Mileage Today", f"{daily_distance:.1f}"],
            ["Truck/Tractor & Trailer Numbers", "TRK-123 / TRL-456", "", "License Plate(s)", "IL-7890"],
            ["Name of Carrier", "ABC Trucking Co.", "", "Home Terminal Address", "123 Main St, Chicago, IL"],
        ]
        top_table = Table(top_data, colWidths=[1.5*inch, 1.5*inch, 0.5*inch, 1.5*inch, 2*inch])
        top_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(top_table)
        elements.append(Spacer(1, 0.1*inch))

        # Duty Status Grid
        drawing = Drawing(7.5*inch, 2*inch)  # Wider and taller for exact 24-hour grid

        # Horizontal lines (4 duty statuses + top/bottom)
        for i in range(5):
            y = i * (2*inch / 4)
            drawing.add(Line(0, y, 7.5*inch, y, strokeColor=colors.black, strokeWidth=0.5))

        # Vertical lines (24 hours with 15-minute increments = 96 segments)
        for i in range(97):  # 96 segments + end line
            x = i * (7.5*inch / 96)
            drawing.add(Line(x, 0, x, 2*inch, strokeColor=colors.black, strokeWidth=0.25 if i % 4 != 0 else 0.5))
            if i % 4 == 0:  # Label every hour
                hour = i // 4
                drawing.add(String(x - 3, 2*inch + 5, str(hour), fontSize=6))

        # "Mid" labels
        drawing.add(String(-15, 2*inch + 5, "Mid", fontSize=6))
        drawing.add(String(7.5*inch - 15, 2*inch + 5, "Mid", fontSize=6))

        # Duty status labels
        statuses = ["1. Off Duty", "2. Sleeper", "3. Driving", "4. On Duty"]
        for i, status in enumerate(statuses):
            y = (3.5 - i) * (2*inch / 4) + 5  # Adjusted for vertical centering
            drawing.add(String(-50, y, status, fontSize=7))

        # Example duty status plot (adjust based on actual trip data)
        times = [0, 8, 10, 18, 24]  # Off Duty 0-8, Driving 8-10, On Duty 10-18, Off Duty 18-24
        status_indices = [0, 2, 3, 0]
        for i in range(len(times) - 1):
            start_time = times[i] * 4  # Convert hours to 15-min increments
            end_time = times[i + 1] * 4
            status_idx = status_indices[i]
            x1 = start_time * (7.5*inch / 96)
            x2 = end_time * (7.5*inch / 96)
            y = (3 - status_idx) * (2*inch / 4) + (2*inch / 8)
            drawing.add(Line(x1, y, x2, y, strokeColor=colors.blue, strokeWidth=1))

        elements.append(drawing)
        elements.append(Spacer(1, 0.1*inch))

        # Remarks and Shipping Documents
        elements.append(Paragraph("Remarks:", normal))
        elements.append(Paragraph(f"Trip from Chicago to Madison, Day {day}", normal))
        elements.append(Spacer(1, 0.05*inch))
        elements.append(Paragraph("Shipping Documents:", normal))
        elements.append(Paragraph("Attached", normal))
        elements.append(Spacer(1, 0.1*inch))

        # End of Day Summary Table
        summary_data = [
            ["end of", "Drivers", "A", "B", "C", "D", "", "60 Hr", "7", "A", "B", "C", "D", "", "if you took"],
            ["day", "Initials", "", "", "", "", "", "Day", "Day", "", "", "", "", "", "consecutive"],
            ["On", "On", "Total", "Total", "Total", "Total", "", "Driven", "Total", "Total", "Total", "Total", "", "hours off"],
            ["Duty", "Duty", "Duty", "Sleeper", "Driving", "On", "", "8", "hours", "Duty", "Sleeper", "Driving", "On", "", "duty in"],
            ["1 & 4", "& 5", "7", "7", "7", "7", "", "hrs", "on", "1 & 4", "7", "7", "7", "", "the last"],
            ["to", "to", "hrs", "hrs", "hrs", "hrs", "", "", "duty", "to", "hrs", "hrs", "hrs", "", "8 days"],
            ["3 & 6", "8", "incl.", "incl.", "incl.", "incl.", "", "", "last", "3 & 6", "incl.", "incl.", "incl.", "", "& 8"],
            ["", "", "", "", "", "", "", "", "8 days", "", "", "", "", "", ""],
        ]
        summary_table = Table(summary_data, colWidths=[0.5*inch]*14 + [1*inch])
        summary_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.1*inch))

        # Footer Instructions
        footer_text = (
            "Enter name of place reported and where released from work and when and where each change of "
            "duty status occurred. If off duty at home terminal, use time standard from work and when."
        )
        elements.append(Paragraph(footer_text, normal))

        # Build PDF
        doc.build(elements)

        logs.append({
            'day': day,
            'pdf': f'/media/daily_logs/daily_log_{trip_id}_day_{day}.pdf',
            'distance': daily_distance,
            'drive_time': daily_drive_time,
            'total_time': daily_time
        })

        remaining_time -= daily_time
        remaining_distance -= daily_distance
        day += 1

    return logs
def generate_eld_log(trip_id, total_time, cycle_used, total_distance):
    logs = []
    remaining_time = total_time
    remaining_distance = total_distance
    day = 1
    
    while remaining_time > 0:
        daily_drive_time = min(11, remaining_time - 2 if day == 1 else remaining_time)
        daily_time = daily_drive_time + (2 if day == 1 else 0)
        daily_distance = (daily_drive_time / total_time) * total_distance if total_time > 0 else 0
        
        plt.figure(figsize=(10, 4))
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
            daily_logs = generate_daily_log(trip.id, total_time, trip.cycle_used, route_data['total_distance'])
            eld_logs = generate_eld_log(trip.id, total_time, trip.cycle_used, route_data['total_distance'])

            
            return Response({
                'route_instructions': route_data['instructions'],
                'total_distance': route_data['total_distance'],
                'total_time': route_data['total_time'],
                'compliance': compliance,
                'daily_logs': daily_logs,
                'eld_logs': eld_logs,
                'coordinates': route_data['coordinates']
            })
        return Response({'error': route_data['error']}, status=400)
    return Response(form.errors, status=400)
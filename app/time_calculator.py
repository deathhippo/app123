# app/plugins/timetable/time_calculator.py
import datetime
import functools
from collections import defaultdict

@functools.lru_cache(maxsize=128)
def calculate_actual_time_totals(events_list_tuple):
    """
    Calculates actual time using a timeline approach to accurately handle
    task switching and lunch deductions.
    """
    events_list = list(events_list_tuple)

    # Group by worker and date
    events_by_worker_day = defaultdict(list)
    for event in events_list:
        # event format: (worker_no, worker_name, datetime_obj, event_type, ref_doc_no)
        if not event[4]: continue
        key = (event[0], event[2].date())
        events_by_worker_day[key].append(event)

    dni_actual_times = defaultdict(float)
    worker_dni_actual_times = defaultdict(lambda: defaultdict(float))

    START_KEYS = ['start', 'začetek', 'zacitek']
    STOP_KEYS = ['stop', 'zaključi', 'zaključek', 'konec', 'zakljuci']

    for (worker_no, date), day_events in events_by_worker_day.items():
        day_events.sort(key=lambda x: x[2])
        
        # 1. Build segments of work
        work_segments = [] # list of (start_time, end_time, dni)
        current_start = None
        current_dni = None
        
        for event in day_events:
            evt_type = str(event[3]).strip().lower()
            evt_time = event[2]
            evt_dni = event[4]
            
            if evt_type in START_KEYS:
                # If we are already working, close the previous segment first (Task Switch)
                if current_start is not None:
                    work_segments.append((current_start, evt_time, current_dni))
                
                # Start new segment
                current_start = evt_time
                current_dni = evt_dni
                
            elif evt_type in STOP_KEYS:
                if current_start is not None:
                    work_segments.append((current_start, evt_time, current_dni))
                    current_start = None
                    current_dni = None

        # Handle forgotten clock-out at end of day
        if current_start is not None:
            # Auto-close at 15:00 if still running
            # But if start was AFTER 15:00, assume 0 duration or valid until now? 
            # Let's stick to the 15:00 rule for consistency with previous logic.
            limit_time = current_start.replace(hour=15, minute=0, second=0, microsecond=0)
            if current_start < limit_time:
                work_segments.append((current_start, limit_time, current_dni))

        # 2. Calculate total raw duration per DNI
        day_dni_totals = defaultdict(float)
        total_day_seconds = 0.0
        
        for start, end, dni in work_segments:
            duration = (end - start).total_seconds()
            if duration > 0:
                day_dni_totals[dni] += duration
                total_day_seconds += duration

        # 3. Analyze Lunch Break (11:00 - 13:00)
        # We look for GAPS between segments in this window.
        lunch_start = datetime.datetime.combine(date, datetime.time(11, 0))
        lunch_end = datetime.datetime.combine(date, datetime.time(13, 0))
        
        # Find gaps
        gaps_in_lunch_window = 0.0
        
        # Check gap before first segment (if started after 11:00)
        if work_segments:
            first_start = work_segments[0][0]
            if first_start > lunch_start:
                 # The gap is from 11:00 to first_start (capped at 13:00)
                 gap_end = min(first_start, lunch_end)
                 if gap_end > lunch_start:
                     gaps_in_lunch_window += (gap_end - lunch_start).total_seconds()

            # Check gap after last segment (if ended before 13:00)
            last_end = work_segments[-1][1]
            if last_end < lunch_end:
                # The gap is from last_end to 13:00 (capped at 11:00 start)
                gap_start = max(last_end, lunch_start)
                if lunch_end > gap_start:
                    gaps_in_lunch_window += (lunch_end - gap_start).total_seconds()

            # Check gaps BETWEEN segments
            for i in range(len(work_segments) - 1):
                seg_end = work_segments[i][1]
                next_start = work_segments[i+1][0]
                
                # Overlap of (seg_end, next_start) with (11:00, 13:00)
                gap_s = max(seg_end, lunch_start)
                gap_e = min(next_start, lunch_end)
                
                if gap_e > gap_s:
                    gaps_in_lunch_window += (gap_e - gap_s).total_seconds()
        
        # 4. Apply Deduction Logic
        # Rule: Deduct remainder of 30 mins if working > 6h
        WORK_THRESHOLD = 21600 # 6 hours
        FULL_BREAK = 1800.0 # 30 mins
        
        deduction_seconds = 0.0
        if total_day_seconds > WORK_THRESHOLD:
            # If gaps are less than 30 mins, deduct the difference
            if gaps_in_lunch_window < FULL_BREAK:
                deduction_seconds = FULL_BREAK - gaps_in_lunch_window
        
        # 5. Distribute deduction proportionally across tasks
        # If we need to deduct 10 mins, we remove it proportionally from all tasks done that day
        adjustment_ratio = 1.0
        if deduction_seconds > 0 and total_day_seconds > 0:
            # Prevent negative time
            if total_day_seconds <= deduction_seconds:
                adjustment_ratio = 0.0
            else:
                adjustment_ratio = (total_day_seconds - deduction_seconds) / total_day_seconds

        # Store final values
        for dni, seconds in day_dni_totals.items():
            final_seconds = seconds * adjustment_ratio
            worker_dni_actual_times[worker_no][dni] += final_seconds
            dni_actual_times[dni] += final_seconds

    final_worker_times = {w: dict(d) for w, d in worker_dni_actual_times.items()}
    final_dni_times = dict(dni_actual_times)

    return final_dni_times, final_worker_times
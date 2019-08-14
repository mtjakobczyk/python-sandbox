import argparse
import random
import datetime
from probabilities import NoEvent
from probabilities import IncidentProbability
from probabilities import AccidentProbability
from dim import LocationDim
from dim import RoadEventDim


def evaluate_probability(success_probability: int):
    rnd = random.randrange(0, 100)
    return int(rnd) <= int(success_probability)


def gre(args):
    # Dimensions
    # Time Dimension
    date_dim_list = []
    with open(args.date_dim_path, 'r') as date_dim_f:
        date_dim_f.readline() # Skip header
        for dt in date_dim_f:
            dt_list = dt.strip().split(',')
            dt_id = dt_list[0]
            dt_date = dt_list[1]
            date_dim_list.append(dt_id)
    print('Loaded '+str(len(date_dim_list))+' Time Dimension rows')

    # Road Dimension
    road_dim_list = []
    with open(args.loc_dim_path, 'r') as road_dim_f:
        road_dim_f.readline() # Skip header
        for road in road_dim_f:
            road_list = road.strip().split(',')
            segment_id = road_list[0]
            road_id = road_list[6]
            segment_type = road_list[2]
            segment_voivodeship = road_list[3]
            ld = LocationDim(segment_id, road_id, segment_type, segment_voivodeship)
            road_dim_list.append(ld)
    print('Loaded '+str(len(road_dim_list))+' Location Dimension rows')

    # Event Dimension
    events_dim_incident_list = []
    events_dim_accident_list = []
    with open(args.rde_dim_path, 'r') as rde_dim_f:
        rde_dim_f.readline() # Skip header
        for rde in rde_dim_f:
            rde_list = rde.strip().split(',')
            event_id = rde_list[0]
            event_name = rde_list[1]
            class_name = rde_list[5]
            rd = RoadEventDim(event_id, event_name, class_name)
            if class_name == 'traffic incident':
                events_dim_incident_list.append(rd)
            if class_name == 'traffic accident':
                events_dim_accident_list.append(rd)
    print('Loaded '+str(len(events_dim_incident_list))+' Road Events (incidents) Dimension rows')
    print('Loaded '+str(len(events_dim_accident_list))+' Road Events (accidents) Dimension rows')

    # Probability Dictionaries
    # NoEvent dictionary
    noevent_dict = {}
    with open(args.noevent_prob_path, 'r') as noevent_prod_f:
        noevent_prod_f.readline()
        for noevent in noevent_prod_f:
            noevent_list = noevent.strip().split(';')
            type = noevent_list[0]
            voivode = noevent_list[1]
            noincident_prob = noevent_list[2]
            noaccident_prob = noevent_list[3]
            ne = NoEvent(type, voivode, noincident_prob, noaccident_prob)
            noevent_dict[ne.bk] = ne
    # IncidentProbability dictionary
    incident_probability_dict = {}
    with open(args.incident_prob_path, 'r') as incident_prob_f:
        incident_prob_f.readline()
        for incident_prob in incident_prob_f:
            incident_prob_list = incident_prob.strip().split(';')
            event_name = incident_prob_list[0]
            road_type = incident_prob_list[1]
            no_event = incident_prob_list[2]
            count_mean = incident_prob_list[3]
            count_stdev = incident_prob_list[4]
            incpr = IncidentProbability(event_name, road_type, no_event, count_mean, count_stdev)
            incident_probability_dict[incpr.bk] = incpr
    # AccidentProbability dictionary
    accident_probability_dict = {}
    with open(args.accident_prob_path, 'r') as accident_prob_f:
        accident_prob_f.readline()
        for accident_prob in accident_prob_f:
            accident_prob_list = accident_prob.strip().split(';')
            event_name = accident_prob_list[0]
            road_type = accident_prob_list[1]
            no_event = accident_prob_list[2]
            count_mean = accident_prob_list[3]
            count_stdev = accident_prob_list[4]
            injured_mean = accident_prob_list[5]
            injured_stdev = accident_prob_list[6]
            killed_mean = accident_prob_list[7]
            killed_stdev = accident_prob_list[8]
            accpr = AccidentProbability(event_name, road_type, no_event, count_mean, count_stdev, injured_mean, injured_stdev, killed_mean, killed_stdev)
            accident_probability_dict[accpr.bk] = accpr

    # Load Probabilities and distributions
    fact_lines = []
    fact_cnt = 0
    first_run = True
    current_year_month_dt = ''
    # For each date
    for dt in date_dim_list:

        if not first_run:
            next_year_month_dt = dt[:4]
            if current_year_month_dt != next_year_month_dt:
                if current_year_month_dt[2:4] in ["06","12"]:
                    write_fact_file(args.fact_files_dir, fact_lines, current_year_month_dt)
                    fact_lines = []

        first_run = False
        current_year_month_dt = dt[:4]

        for road in road_dim_list:
            # Evaluate no incidents at all at the processed location
            no_incident = evaluate_probability(noevent_dict[road.getbk()].no_incident_prob)
            if no_incident:
                continue
            # Generate incidents
            for incident in events_dim_incident_list:
                # Evaluate no incident of a specific type at the processed location
                incident_prob_key = incident.name + ':' + road.road_type
                incident_probability = incident_probability_dict[incident_prob_key]
                no_incident = evaluate_probability(incident_probability.no_event)
                if no_incident:
                    continue
                # Generate incident count for the specific incident type at the processed location
                incident_count = int(incident_probability.random_count())
                fact_lines.append(dt+';'+road.location_id+';'+incident.id+';'+str(incident_count)+';0;0\n')
                fact_cnt += 1
            # Evaluate no accidents at all at the processed location
            no_accident = evaluate_probability(noevent_dict[road.getbk()].no_accident_prob)
            if no_accident:
                continue
            # Generate accidents
            for accident in events_dim_accident_list:
                # Evaluate no accidents of a specific type at the processed location
                accident_prob_key = accident.name + ':' + road.road_type
                accident_probability = accident_probability_dict[accident_prob_key]
                no_accident = evaluate_probability(accident_probability.no_event)
                if no_accident:
                    continue
                # Generate accident, injured and killed counts for the specific accident type at the location
                accident_count = accident_probability.random_count()
                accident_injured = accident_probability.random_injured()
                accident_killed = accident_probability.random_killed()
                counts_str = str(accident_count)+';'+str(accident_injured)+';'+str(accident_killed)
                fact_lines.append(dt+';'+road.location_id+';'+accident.id+';'+counts_str+'\n')
                fact_cnt += 1
    write_fact_file(args.fact_files_dir, fact_lines, current_year_month_dt)
    print('Generated '+str(fact_cnt)+' fact rows')


def write_fact_file(fact_files_dir, fact_lines, current_year_month_dt):
    half_year_month_map = {
        '06': 'H1',
        '12': 'H2'
    }
    current_year_dt = current_year_month_dt[:2]
    current_month_dt = current_year_month_dt[2:4]
    fact_file_suffix = current_year_dt + half_year_month_map[current_month_dt]
    fact_files_filename = fact_files_dir + '/facts.' + fact_file_suffix + '.csv'
    with open(fact_files_filename, 'w') as fact_file_f:
        fact_file_f.write('time_dim_id;road_dim_id;event_dim_id;count;injured;killed\n')
        for line in fact_lines:
            fact_file_f.write(line)
    print('Written ' + str(len(fact_lines)) + ' fact rows to ' + fact_files_filename)


def main():
    parser = argparse.ArgumentParser(description="Convert a fastA file to a FastQ file")
    parser.add_argument("--date_dim_path", help="Date Dimension File", dest="date_dim_path", type=str, required=True)
    parser.add_argument("--event_dim_path", help="Road Event Dimension File", dest="rde_dim_path", type=str, required=True)
    parser.add_argument("--location_dim_path", help="Location Dimension File", dest="loc_dim_path", type=str, required=True)
    parser.add_argument("--noevent_prob_path", help="No Event Probability File", dest="noevent_prob_path", type=str, required=True)
    parser.add_argument("--incident_prob_path", help="Incident Probability File", dest="incident_prob_path", type=str, required=True)
    parser.add_argument("--accident_prob_path", help="Accident Probability File", dest="accident_prob_path", type=str, required=True)
    parser.add_argument("--fact_files_dir", help="Fact Files dir", dest="fact_files_dir", type=str, required=True)
    gre(parser.parse_args())


if __name__ == "__main__":
    start_dt = datetime.datetime.now()
    print('Start: '+str(start_dt))
    main()
    end_dt = datetime.datetime.now()
    print('Finished: '+str(end_dt))
    duration = end_dt - start_dt
    print('Execution time: '+str(duration))

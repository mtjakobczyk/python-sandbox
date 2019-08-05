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
            dt_list = dt.strip().split(';')
            dt_id = dt_list[0]
            dt_date = dt_list[1]
            date_dim_list.append(dt_id)
    print('Loaded '+str(len(date_dim_list))+' Time Dimension rows')

    # Location Dimension
    location_dim_list = []
    with open(args.loc_dim_path, 'r') as loc_dim_f:
        loc_dim_f.readline() # Skip header
        for loc in loc_dim_f:
            loc_list = loc.strip().split(';')
            loc_id = loc_list[0]
            loc_road = loc_list[1]
            loc_type = loc_list[2]
            loc_voivode = loc_list[3]
            ld = LocationDim(loc_id, loc_road, loc_type, loc_voivode)
            location_dim_list.append(ld)
    print('Loaded '+str(len(location_dim_list))+' Location Dimension rows')

    # Road Events Dimension
    events_dim_incident_list = []
    events_dim_accident_list = []
    with open(args.rde_dim_path, 'r') as rde_dim_f:
        rde_dim_f.readline() # Skip header
        for rde in rde_dim_f:
            rde_list = rde.strip().split(';')
            rde_id = rde_list[0]
            rde_event_name = rde_list[1]
            rde_event_category = rde_list[3]
            rd = RoadEventDim(rde_id, rde_event_name, rde_event_category)
            if rde_event_category == 'traffic incident':
                events_dim_incident_list.append(rd)
            if rde_event_category == 'traffic accident':
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

    # Write fact file header
    with open(args.fact_file_path, 'w') as fact_file_f:
        fact_file_f.write('date_dim_id;location_dim_id;road_event_dim_id;count;injured;killed\n')

        fact_cnt = 0
        # For each date
        for dt in date_dim_list:
            for loc in location_dim_list:
                # Evaluate no incidents at all at the processed location
                no_incident = evaluate_probability(noevent_dict[loc.getbk()].no_incident_prob)
                if no_incident:
                    continue
                # Generate incidents
                for incident in events_dim_incident_list:
                    # Evaluate no incident of a specific type at the processed location
                    incident_prob_key = incident.name + ':' + loc.road_type
                    incident_probability = incident_probability_dict[incident_prob_key]
                    no_incident = evaluate_probability(incident_probability.no_event)
                    if no_incident:
                        continue
                    # Generate incident count for the specific incident type at the processed location
                    incident_count = int(incident_probability.random_count())
                    fact_file_f.write(dt+';'+loc.location_id+';'+incident.id+';'+str(incident_count)+';0;0\n')
                    fact_cnt += 1
                # Evaluate no accidents at all at the processed location
                no_accident = evaluate_probability(noevent_dict[loc.getbk()].no_accident_prob)
                if no_accident:
                    continue
                # Generate accidents
                for accident in events_dim_accident_list:
                    # Evaluate no accidents of a specific type at the processed location
                    accident_prob_key = accident.name + ':' + loc.road_type
                    accident_probability = accident_probability_dict[accident_prob_key]
                    no_accident = evaluate_probability(accident_probability.no_event)
                    if no_accident:
                        continue
                    # Generate accident, injured and killed counts for the specific accident type at the location
                    accident_count = accident_probability.random_count()
                    accident_injured = accident_probability.random_injured()
                    accident_killed = accident_probability.random_killed()
                    counts_str = str(accident_count)+';'+str(accident_injured)+';'+str(accident_killed)
                    fact_file_f.write(dt+';'+loc.location_id+';'+accident.id+';'+counts_str+'\n')
                    fact_cnt += 1
    print('Written '+str(fact_cnt)+' fact rows')


def main():
    parser = argparse.ArgumentParser(description="Convert a fastA file to a FastQ file")
    parser.add_argument("--date_dim_path", help="Date Dimension File", dest="date_dim_path", type=str, required=True)
    parser.add_argument("--event_dim_path", help="Road Event Dimension File", dest="rde_dim_path", type=str, required=True)
    parser.add_argument("--location_dim_path", help="Location Dimension File", dest="loc_dim_path", type=str, required=True)
    parser.add_argument("--noevent_prob_path", help="No Event Probability File", dest="noevent_prob_path", type=str, required=True)
    parser.add_argument("--incident_prob_path", help="Incident Probability File", dest="incident_prob_path", type=str, required=True)
    parser.add_argument("--accident_prob_path", help="Accident Probability File", dest="accident_prob_path", type=str, required=True)
    parser.add_argument("--fact_file", help="Fact Table File path", dest="fact_file_path", type=str, required=True)
    gre(parser.parse_args())


if __name__ == "__main__":
    start_dt = datetime.datetime.now()
    print('Start: '+str(start_dt))
    main()
    end_dt = datetime.datetime.now()
    print('Finished: '+str(end_dt))
    duration = end_dt - start_dt
    print('Execution time: '+str(duration))

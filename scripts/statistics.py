import pandas
import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def get_events_names(data_dir):
    file_names = os.listdir(data_dir)
    events = []
    for file_name in file_names:
        print()
        if file_name[-3:] == 'pdf':
            events.append(file_name[:-14])
    events = list(set(events))
    events.sort(reverse=False)
    return events


def main():

    # dirs
    dir_trajs_filtered = '../data/trajectories_filtered/'

    pandas.set_option('display.max_columns', 15)

    all_ped_v_abs = []
    all_veh_psi = []
    # process each file (data)
    scenarios = os.listdir(dir_trajs_filtered)
    for scenario in scenarios:
        events = get_events_names(Path(dir_trajs_filtered, scenario))
        for event in events:
            # load trajs
            df_peds = pandas.read_csv(Path(dir_trajs_filtered, scenario, event + '_traj_ped_filtered.csv'))
            # pedestrian statistics
            df_peds['v_abs_sq'] = df_peds.vx_est**2 + df_peds.vy_est**2
            df_peds['v_abs'] = df_peds['v_abs_sq'].apply(np.sqrt)
            all_ped_v_abs.append(df_peds['v_abs'])
            # vehicle statistics
            if scenario[0] == 'v':
                df_vehs = pandas.read_csv(Path(dir_trajs_filtered, scenario, event + '_traj_veh_filtered.csv'))
                veh_ids = list(df_vehs.id.unique())
                for id in veh_ids:
                    all_veh_psi.append(df_vehs[df_vehs.id == id]['psi_est'].reset_index(drop=True).diff(periods=1))

    all_ped_v_abs = pandas.concat(all_ped_v_abs)


    # abs velocity dist
    plt.figure(0)
    plt.hist(all_ped_v_abs, color='blue', edgecolor='black', bins=100)
    # Add labels
    plt.title('Histogram of Absolute Velocity')
    plt.xlabel('Velocity (m/s)')
    plt.ylabel('Counts')
    plt.axis([0, 3, 0, 7000])
    plt.show()
    # plt.savefig('ped_velocity_dist.pdf', format='pdf', dpi=1000)

    # mean abs velocity
    print('Mean abs velocity is: ', np.mean(all_ped_v_abs))
    print('Trimmed Mean abs velocity is: ', np.mean(all_ped_v_abs[all_ped_v_abs>0.3]))

    plt.figure(1)
    for psi in all_veh_psi:
        plt.plot(psi, '.')
    # Add labels
    plt.title('Heading Angle Change of All Vehicles')
    plt.xlabel('Time')
    plt.ylabel('Heading Change (rad)')
    plt.ylim([-0.05, 0.05])
    # plt.axis([0, 3, 0, 30000])
    plt.show()
    # plt.savefig('veh_heading_change.pdf', format='pdf', dpi=1000)


if __name__ == '__main__':
    main()
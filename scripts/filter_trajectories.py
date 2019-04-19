import os
import pandas
import matplotlib.pyplot as plt
import numpy as np
import datetime
from pathlib import Path
import pandas as pd

from tools.kalman_filters import LinearPointMass, NonlinearKinematicBicycle


def get_scenarios_names(data_dir):
    file_names = os.listdir(data_dir)
    scenarios = [file_name[:-13] for file_name in file_names]
    scenarios = list(set(scenarios))
    scenarios.sort(reverse=False)
    return scenarios


def mkdir_anyway(new_dir):
    if not os.path.isdir(new_dir):
        os.makedirs(new_dir)
    return None


def main():
    # dirs
    dir_trajs_raw = '../data/trajectories/'
    dir_trajs_filtered = '../data/trajectories_filtered/'

    # params
    fps = 29.97
    dt = 1/fps

    pandas.set_option('display.max_columns', 10)

    # initialize Kalman filters
    filter_ped = LinearPointMass(dt=dt)
    filter_veh = NonlinearKinematicBicycle(lf=1.2, lr=1.0, dt=dt)

    # process each file (data)
    scenarios = os.listdir(dir_trajs_raw)
    for scenario in scenarios:
        events = os.listdir(Path(dir_trajs_raw, scenario))
        for event in events:
            print('-processing', event, '...')

            mkdir_anyway(Path(dir_trajs_filtered, scenario))

            df_peds = []
            df_vehs = []

            plt.figure(1)

            for file in os.listdir(Path(dir_trajs_raw, scenario, event)):
                if file[-3:] == 'csv':
                    if file[0] == 'p':
                        print('--filtering', file[0:-4], '...')

                        df_ped = pd.read_csv(Path(dir_trajs_raw, scenario, event, file))

                        # plot orginal
                        plt.plot(df_ped.x, df_ped.y)

                        id_frames = list(df_ped.frame)
                        for i, id_frame in enumerate(id_frames):

                            id_dataframe = int(df_ped[df_ped.frame == id_frame].index.values)

                            if i == 0:  # initalize KF
                                df_ped.loc[id_dataframe, 'x_est'] = float(df_ped.loc[id_dataframe, 'x'])
                                df_ped.loc[id_dataframe, 'vx_est'] = (float(df_ped[df_ped.frame == id_frame + 1].x)
                                                                       - float(df_ped[df_ped.frame == id_frame].x)) / (
                                                                                  1 * dt)
                                df_ped.loc[id_dataframe, 'y_est'] = float(df_ped.loc[id_dataframe, 'y'])
                                df_ped.loc[id_dataframe, 'vy_est'] = (float(df_ped[df_ped.frame == id_frame + 1].y)
                                                                       - float(df_ped[df_ped.frame == id_frame].y)) / (
                                                                                  1 * dt)
                                P_matrix = np.identity(4)

                            elif i < len(id_frames):
                                # assign new est values
                                df_ped.loc[id_dataframe, 'x_est'] = x_vec_est_new[0][0]
                                df_ped.loc[id_dataframe, 'vx_est'] = x_vec_est_new[1][0]
                                df_ped.loc[id_dataframe, 'y_est'] = x_vec_est_new[2][0]
                                df_ped.loc[id_dataframe, 'vy_est'] = x_vec_est_new[3][0]

                            if i < len(id_frames) - 1:  # no action on last data
                                # filtering
                                x_vec_est = np.array([[df_ped.loc[id_dataframe].x_est],
                                                      [df_ped.loc[id_dataframe].vx_est],
                                                      [df_ped.loc[id_dataframe].y_est],
                                                      [df_ped.loc[id_dataframe].vy_est]])
                                z_new = np.array([[float(df_ped[df_ped.frame == id_frame + 1].x)],
                                                  [float(df_ped[df_ped.frame == id_frame + 1].y)]])
                                x_vec_est_new, P_matrix_new = filter_ped.predict_and_update(
                                    x_vec_est=x_vec_est,
                                    u_vec=np.array([[0.], [0.]]),
                                    P_matrix=P_matrix,
                                    z_new=z_new
                                )
                                P_matrix = P_matrix_new

                        # plot filtered
                        plt.plot(df_ped.x_est, df_ped.y_est, 'k', lw=1)

                        df_peds.append(df_ped)
                    elif file[0] == 'v':
                        print('--filtering', file[0:-4], '...')

                        df_veh = pd.read_csv(Path(dir_trajs_raw, scenario, event, file))

                        # plot orginal
                        plt.plot(df_veh.x_c, df_veh.y_c)

                        id_frames = list(df_veh.frame)
                        for i, id_frame in enumerate(id_frames):

                            id_dataframe = int(df_veh[df_veh.frame == id_frame].index.values)
                            if i == 0:  # initalize KF

                                # initial x, y
                                df_veh.loc[id_dataframe, 'x_est'] = float(df_veh.loc[id_dataframe, 'x_c'])
                                df_veh.loc[id_dataframe, 'y_est'] = float(df_veh.loc[id_dataframe, 'y_c'])

                                # estimating initial velocity
                                if len(id_frames) < 11:  # increment for estimating initial velocity
                                    increment = len(id_frames) - 1
                                else:
                                    increment = 10
                                vx = (float(df_veh[df_veh.frame == id_frame + increment].x_c)
                                      - float(df_veh[df_veh.frame == id_frame].x_c)) / (increment * dt)
                                vy = (float(df_veh[df_veh.frame == id_frame + increment].y_c)
                                      - float(df_veh[df_veh.frame == id_frame].y_c)) / (increment * dt)
                                df_veh.loc[id_dataframe, 'vel_est'] = np.linalg.norm([[vx], [vy]])
                                print('initial velocity:', np.linalg.norm([[vx], [vy]]))

                                # estimating initial heading angle
                                p1 = np.array([[df_veh.loc[id_dataframe, 'x_1']], [df_veh.loc[id_dataframe, 'y_1']]])
                                p2 = np.array([[df_veh.loc[id_dataframe, 'x_2']], [df_veh.loc[id_dataframe, 'y_2']]])
                                vec_heading = p1 - p2
                                df_veh.loc[id_dataframe, 'psi_est'] = np.arctan2(vec_heading[1][0], vec_heading[0][0])
                                print('initial heading angle:', np.arctan2(vy, vx),
                                      np.arctan2(vec_heading[1][0], vec_heading[0][0]))
                                # df_vehs.loc[id_dataframe, 'psi_est'] = np.arctan2(vy, vx)

                                # initial P_matrix
                                P_matrix = np.identity(4)

                            elif i < len(id_frames):
                                # assign new est values
                                df_veh.loc[id_dataframe, 'x_est'] = x_vec_est_new[0][0]
                                df_veh.loc[id_dataframe, 'y_est'] = x_vec_est_new[1][0]
                                df_veh.loc[id_dataframe, 'psi_est'] = x_vec_est_new[2][0]
                                df_veh.loc[id_dataframe, 'vel_est'] = x_vec_est_new[3][0]

                            if i < len(id_frames) - 1:  # no action on last data
                                # filtering
                                x_vec_est = np.array([[df_veh.loc[id_dataframe].x_est],
                                                      [df_veh.loc[id_dataframe].y_est],
                                                      [df_veh.loc[id_dataframe].psi_est],
                                                      [df_veh.loc[id_dataframe].vel_est]])
                                z_new = np.array([[float(df_veh[df_veh.frame == id_frame + 1].x_c)],
                                                  [float(df_veh[df_veh.frame == id_frame + 1].y_c)]])
                                x_vec_est_new, P_matrix_new = filter_veh.predict_and_update(
                                    x_vec_est=x_vec_est,
                                    u_vec=np.array([[0.], [0.]]),
                                    P_matrix=P_matrix,
                                    z_new=z_new
                                )
                                P_matrix = P_matrix_new

                        plt.plot(df_veh.x_est,
                                 df_veh.y_est, 'k', lw=2)

                        df_vehs.append(df_veh)
                elif file[-3:] == 'txt':
                    ratio = Path(dir_trajs_raw, scenario, event, file).read_text()
                    # save ratio file
                    Path(dir_trajs_filtered, scenario, event +'_' + file).write_text(ratio)
                    plt.xlim((0, 1920 / float(ratio)))
                    plt.ylim((0, 1080 / float(ratio)))

            # SAVE DATA

            # get time
            time = datetime.datetime.now()
            current_time = str(time.strftime(" %Y-%m-%d %H-%M-%S"))

            # save traj plot
            if os.path.isfile(Path(dir_trajs_filtered, scenario, event + '_traj_plot.pdf')):
                plt.savefig(Path(dir_trajs_filtered, scenario, event + '_traj_plot' + current_time + '.pdf'), bbox_inches='tight')
            else:
                plt.savefig(Path(dir_trajs_filtered, scenario, event + '_traj_plot.pdf'), bbox_inches='tight')
            plt.clf()

            # write ped csv
            df_peds = pd.concat(df_peds)
            df_peds['label'] = df_peds.type
            df_peds = df_peds[['id', 'frame', 'label', 'x_est', 'y_est', 'vx_est', 'vy_est']]
            if os.path.isfile(Path(dir_trajs_filtered, scenario, event + '_traj_ped_filtered.csv')):
                print('ped traj file existed, current time is appended to the file name ...')
                df_peds.to_csv(Path(dir_trajs_filtered, scenario, event + '_traj_ped_filtered' + current_time + '.csv'),
                               index=False)
            else:
                df_peds.to_csv(Path(dir_trajs_filtered, scenario, event + '_traj_ped_filtered.csv'), index=False)

            # write veh csv
            if not len(df_vehs) == 0:
                df_vehs = pd.concat(df_vehs)
                df_vehs['label'] = df_vehs.type
                df_vehs = df_vehs[['id', 'frame', 'label', 'x_est', 'y_est', 'psi_est', 'vel_est']]
                if os.path.isfile(Path(dir_trajs_filtered, scenario, event + '_traj_veh_filtered.csv')):
                    print('veh traj file existed, current time is appended to the file name ...')
                    df_vehs.to_csv(Path(dir_trajs_filtered, scenario, event + '_traj_veh_filtered' + current_time + '.csv'),
                                   index=False)
                else:
                    df_vehs.to_csv(Path(dir_trajs_filtered, scenario, event + '_traj_veh_filtered.csv'), index=False)#




if __name__ == '__main__':
    main()

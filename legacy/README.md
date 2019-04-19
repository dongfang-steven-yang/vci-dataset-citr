## Dataset Description Legacy

### Folders
- The folder is named as the name of a particular sceanrio. It contains the trajectories of all pedestrians and vehicles.

### Figures
- You may refer to "result_peds.svg" and "result_vehs.svg" for the details of Kalman filtering result.

### Pedestrians
- Inside a particular sceanrio, the trajectory of each pedestrian is stored in "p*.csv" file. Here "*" stands for the serial number of the pedestrian. Note among all scenarios, a pedestrian with the same serial number indifies the same pedestrian.
- In the ".csv" file, the first row is the header. In each of the following rows, entries from left to right represnet:

```
frame: frame number from the video clip
x_measure: tracked x position in pixels (unfiltered)
y_measure: tracked y position in pixels (unfiltered)
x_est: x position estimated by Kalman filter
y_est: y position estimated by Kalman filter
vx_est: x velocity estimated by Kalman filter 
vy_est: y velocity estimated by Kalman filter
```

- You may need to truncate the trajectory if necessary, especially if you are using the estimated velocity. Since we don't have direct measurement for velocities, if a pedestrian stops moving, the estimated velocity out of Kalman filter becomes less accurate. Please check the figures for detailed filtering result.

### Vehicles
- Inside a particular sceanrio, the trajectory of each vehicle is stored in "v*.csv" file. Here "*" stands for the serial number of the vehicle. Since usually there is only one vehicle, you will only see "v1.csv". If there is no vehicle in the scenario, you won't see any file starting with "v".
- The vehicle is tracked by two markers on the vehicle top in the video: center marker and front marker. To obtain the vehicle trajectory, the middle point between these two markers is calculated. 
- Below is a rough measure of the vehicle shape. If you need precision, please refer to the updated "README" file.
```
                   right side                             
                       |
                      0.6m
                       |
front bumper -- 1m -- P_mid_measure -- 1.2m -- rear bumper
                       |
                      0.6m
                       |
                   left side 
```

- In the ".csv" file, the first row is the header. In each of the following rows, entries from left to right represnet:

```
frame: frame number from the video clip
x_measure: tracked x position of the vehicle center marker in pixels (unfiltered)
y_measure: tracked y position of the vehicle center marker in pixels (unfiltered)
x_front_measure: tracked x position of the vehicle front marker in pixels (unfiltered)
y_front_measure: tracked y position of the vehicle front markerin pixels (unfiltered)
x_mid_measure: x position of the middle point between above center and front markers (unfiltered)
y_mid_measure: y position of the middle point between above center and front markers (unfiltered)
x_mid_est: x position of the middle point estimated by Kalman filter
y_mid_est: y position of the middle point estimated by Kalman filter
vx_mid_est: x velocity of the middle point estimated by Kalman filter 
vy_mid_est: y velocity of the middle point estimated by Kalman filter
```

- Note that for vehicle trajectory, only middle point is filtered. 
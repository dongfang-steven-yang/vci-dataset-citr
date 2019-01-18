%% data visualization
% Dongfang Yang
% 2019-01-18

clear all
close all
clc

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Please select following parameters
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% step 1: select scenario name
scenario_name = 'back_interaction_01';

% step 2: select if you woudl like to generate a demo video:
record_enable = 1; % 1: yes; 0: no.
% step 3: select if you would like to visualize the result in matlab
vis = 'off';
% vis = 'on';


%% Reading data
% obtain file names
csv_peds = dir(['trajectory_filtered/',scenario_name,'/p*.csv']);
csv_vehs = dir(['trajectory_filtered/',scenario_name,'/v*.csv']);

formatSpecPeds = '%d%f%f%f%f%f%f';
for p = 1:length(csv_peds)
    data_ped_filename = strcat('trajectory_filtered/',scenario_name, '/',csv_peds(p).name);
    data_ped{p} = readtable(data_ped_filename, 'Delimiter',',','Format',formatSpecPeds);
end

formatSpecVehs = '%d%f%f%f%f%f%f%f%f%f%f';
for v = 1:length(csv_vehs)
    data_veh_filename = strcat('trajectory_filtered/',scenario_name, '/',csv_vehs(v).name);
    data_veh{v} = readtable(data_veh_filename, 'Delimiter',',','Format',formatSpecVehs);
end

% read ratio file
if length(csv_vehs) == 0
    ratio_filename = ['trajectory_filtered/',scenario_name, '/ratio_pixel2meter_ground.txt'];
else
    ratio_filename = ['trajectory_filtered/',scenario_name, '/ratio_pixel2meter.txt'];
end

ratio = load(ratio_filename);

% video
frame_ind = 0; % frame index in video
video_filename = strcat('stabilized_videos/stabilized_',scenario_name,'.mp4');
video = VideoReader(video_filename);
fps = video.FrameRate;

if record_enable
    date_time = datestr(now,'yyyy-mm-dd-HH-MM'); 
    record = VideoWriter(['demo_videos/demo_',scenario_name,'_',date_time,'.avi']);
    record.FrameRate = fps;
    open(record)
end


frame_start = min(data_ped{1}.frame);
frame_end = max(data_ped{1}.frame);
frame_current = frame_start;

% figure property
c = 1.5;
figure('Visible', vis, 'Position', [100 100 960*c 540*c])
axis([0 1920 0 1080])
set(gca,'Ydir','reverse')

while frame_ind < frame_end
    % skip unannotated frames
    while frame_ind < frame_start
        frame_v = readFrame(video);
        frame_ind = frame_ind + 1;
    end
    
    image(frame_v);
    hold on
    % plot peds
    for p = 1:length(csv_peds)
        dpx = ratio * data_ped{p}.x_est(data_ped{p}.frame==frame_ind);
        dpy = ratio * data_ped{p}.y_est(data_ped{p}.frame==frame_ind);
        plot(dpx, dpy, 'o', 'color',[p/8 0.8 0.8],'LineWidth',3);
    end
    % plot vehs
    for v = 1:length(csv_vehs)
        dpx = ratio * data_veh{v}.x_mid_est(data_veh{v}.frame==frame_ind);
        dpy = ratio * data_veh{v}.y_mid_est(data_veh{v}.frame==frame_ind);
        plot(dpx, dpy, 'o', 'color',[1 0 0],'LineWidth',3);
    end
    % plot frame number
    text(10,10,['frame ',num2str(frame_ind)],'Color',[1 0 0])
    
    if record_enable
        disp(['saving frame ',num2str(frame_ind),'...'])
        frame_record = getframe(gcf);
        writeVideo(record,frame_record);
    end
    
    hold off
    pause(1/fps)
    hold on
    
    if frame_ind > frame_end
        break;
    end
    % get next frame
    frame_v = readFrame(video);
    frame_ind = frame_ind + 1;
end

if record_enable
    close(record)
end

import configparser

config = configparser.ConfigParser()
config['CIF'] =  {'cif_path':'C:/Google Drive/Documents/Manuscripts/TMDCs on sapphire/DFT/Buffer Layer/S-CONTCAR-No-Buffer.cif',
                  'destination':'C:/Google Drive/Documents/RHEED/RHEED simulation results/MoS2 on sapphire IV 10182019/',
                  'h_range':3,
                  'k_range':3,
                  'l_range':1,
                  'shape':'Circle',
                  'lateral_size':3,
                  'X_shift':0,
                  'Y_shift':0,
                  'Z_shift':0,
                  'rotation':0,
                  'Z_min': '1,1.5,3,4,5,6,7,8,9,10,11,12,14,17,19,20',
                  'Z_max':21,
                  'number_of_K_para_steps':1,
                  'number_of_K_perp_steps':1000,
                  'Kx_range_min':0,
                  'Kx_range_max':0,
                  'Ky_range_min':0,
                  'Ky_range_max':0,
                  'Kz_range_min':0,
                  'Kz_range_max':10,
                  'camera_horizontal_rotation':0,
                  'camera_vertical_rotation':8,
                  'camera_zoom_level':150,
                  'plot_font_size':7,
                  'plot_log_scale':'True',
                  'do_FFT_for_IV':'True',
                  'save_scene':'False',
                  'save_zoomed_scene':'False',
                  'save_IV_image':'True',
                  'save_IV_data':'True',
                  'constant_af':'True',
                  'lattice_or_atoms':'lattice',
                  'calculate_diffraction':'True',
                  }

config['TAPD'] = {'epi_cif_path':'C:/Google Drive/Documents/CIF/MoS2_3.15.cif',
                  'sub_cif_path':'C:/Google Drive/Documents/CIF/Sapphire_4.76.cif', 
                  'destination':'C:/Google Drive/Documents/RHEED/RHEED simulation results/MoS2 TAPD 08262019/',
                  'x_max':350,
                  'y_max':350,
                  'z_min':0,
                  'z_max':0.5,
                  'x_shift':0,
                  'y_shift':0,
                  'z_shift':8,
                  'buffer_x_shift':0,
                  'buffer_y_shift':0,
                  'buffer_z_shift':-3,
                  'number_of_K_para_steps':500,
                  'number_of_K_perp_steps':1,
                  'Kx_range_min':-3,
                  'Kx_range_max':3,
                  'Ky_range_min':-3,
                  'Ky_range_max':3,
                  'Kz_range_min':0,
                  'Kz_range_max':10,
                  'camera_horizontal_rotation':0,
                  'camera_vertical_rotation':90,
                  'camera_zoom_level':190,
                  'plot_font_size':30,
                  'add_atoms':'False',
                  'add_substrate':'False',
                  'add_epilayer':'False',
                  'add_buffer':'False',
                  'calculate_diffraction':'False',
                  'plot_log_scale':'False',
                  'save_size_distribution':'True',
                  'save_boundary_statistics':'True',
                  'save_boundary':'False',
                  'save_voronoi_diagram':'False',
                  'save_scene':'False',
                  'save_2D_map_image':'False',
                  'save_2D_map_data':'False',
                  'constant_af':'True',
                  'sub_orientation':'(001)',
                  'epi_orientation':'(001)',
                  'lattice_or_atoms':'lattice',
                  'colormap':'jet',
                  'distribution':'completely random',
                  'density':0.001,
                  'buffer_atom':'S',
                  'buffer_in_plane_distribution':'completely random',
                  'buffer_in_plane_density':1,
                  'buffer_out_of_plane_distribution':'gaussian',
                  'buffer_out_of_plane_low':-0.5,
                  'buffer_out_of_plane_high':0.5
                  }

with open('./default_scenario.ini','w') as configfile:
    config.write(configfile)

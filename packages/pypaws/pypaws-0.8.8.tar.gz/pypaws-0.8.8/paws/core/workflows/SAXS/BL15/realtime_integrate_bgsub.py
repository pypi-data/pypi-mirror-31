import os
from collections import OrderedDict

import paws
from paws.core.workflows.WfManager import WfManager
from paws.core import pawstools

# specify workflow names: 
wf_names = ['background_process','sample_process','main']
# specify operation names and corresponding modules: 
op_maps = OrderedDict.fromkeys(wf_names)
for wf_name in wf_names:
    op_maps[wf_name] = OrderedDict()
op_maps['main']['read_calibration'] = 'IO.CALIBRATION.NikaToPONI'
op_maps['main']['build_integrator'] = 'PROCESSING.INTEGRATION.BuildPyFAIIntegrator'
op_maps['main']['background_files'] = 'IO.FILESYSTEM.BuildFileList'
op_maps['main']['background_batch'] = 'EXECUTION.Batch'
op_maps['main']['sample_files'] = 'IO.FILESYSTEM.FileIterator'
op_maps['main']['sample_realtime'] = 'EXECUTION.Realtime'

op_maps['background_process']['read_header'] = 'IO.BL15.ReadHeader_SSRL15'
op_maps['background_process']['time_temp'] = 'PACKAGING.BL15.TimeTempFromHeader'
op_maps['background_process']['image_path'] = 'IO.FILESYSTEM.BuildFilePath'
op_maps['background_process']['read_image'] = 'IO.IMAGE.FabIOOpen'
op_maps['background_process']['integrate'] = 'PROCESSING.INTEGRATION.ApplyIntegrator1d'
op_maps['background_process']['q_window'] = 'PACKAGING.Window'
op_maps['background_process']['dezinger'] = 'PROCESSING.ZINGERS.EasyZingers1d'
op_maps['background_process']['log_I'] = 'PROCESSING.BASIC.LogY'
op_maps['background_process']['output_CSV'] = 'IO.CSV.WriteArrayCSV'

op_maps['sample_process']['read_header'] = 'IO.BL15.ReadHeader_SSRL15'
op_maps['sample_process']['time_temp'] = 'PACKAGING.BL15.TimeTempFromHeader'
op_maps['sample_process']['image_path'] = 'IO.FILESYSTEM.BuildFilePath'
op_maps['sample_process']['read_image'] = 'IO.IMAGE.FabIOOpen'
op_maps['sample_process']['integrate'] = 'PROCESSING.INTEGRATION.ApplyIntegrator1d'
op_maps['sample_process']['q_window'] = 'PACKAGING.Window'
op_maps['sample_process']['dezinger'] = 'PROCESSING.ZINGERS.EasyZingers1d'
op_maps['sample_process']['bg_subtract'] = 'PROCESSING.BACKGROUND.BgSubtractByTemperature'
op_maps['sample_process']['log_I'] = 'PROCESSING.BASIC.LogY'
op_maps['sample_process']['output_CSV'] = 'IO.CSV.WriteArrayCSV'

wfmgr = WfManager()
# add the workflows and activate/add the operations:
for wf_name,op_map in op_maps.items():
    wfmgr.add_workflow(wf_name)
    for op_name,op_uri in op_map.items():
        op = wfmgr.op_manager.get_operation(op_uri)
        wfmgr.workflows[wf_name].add_operation(op_name,op)



wf = wfmgr.workflows['main']

# input 0: path to calibration file 
wf.set_op_input('read_calibration','file_path',None)
wf.connect_input('nika_file','read_calibration.inputs.file_path')

# input 1: path to background header files directory
wf.set_op_input('background_files','dir_path',None)
wf.connect_input('background_dir','background_files.inputs.dir_path')

# input 2: regex for background header files 
wf.set_op_input('background_files','regex','*.txt')
wf.connect_input('background_regex','background_files.inputs.regex')

# input 3: path to sample header files directory
wf.set_op_input('sample_files','dir_path',None)
wf.connect_input('sample_dir','sample_files.inputs.dir_path')

# input 4: regex for sample header files 
wf.set_op_input('sample_files','regex','*.txt')
wf.connect_input('sample_regex','sample_files.inputs.regex')

# input 5: whether or not to process new files
wf.set_op_input('sample_files','new_files_only',False)
wf.connect_input('new_files_only','sample_files.inputs.new_files_only')

# input 6: maximum delay for realtime to bail 
wf.set_op_input('sample_realtime','max_delay',100000)
wf.connect_input('max_delay','sample_realtime.inputs.max_delay')

wf.set_op_input('build_integrator','poni_dict','read_calibration.outputs.poni_dict','workflow item')

wf.set_op_input('background_batch','work_item','background_process','entire workflow')
wf.set_op_input('background_batch','input_arrays',['background_files.outputs.file_list'],'workflow item')
wf.set_op_input('background_batch','input_keys',['header_file'])
wf.set_op_input('background_batch','static_inputs',['build_integrator.outputs.integrator'],'workflow item')
wf.set_op_input('background_batch','static_input_keys',['integrator'])

wf.set_op_input('sample_realtime','work_item','sample_process','entire workflow')
wf.set_op_input('sample_realtime','input_generators',['sample_files.outputs.file_iterator'],'workflow item')
wf.set_op_input('sample_realtime','input_keys',['header_file'])
wf.set_op_input('sample_realtime','static_inputs',
    ['build_integrator.outputs.integrator',
     'background_batch.outputs.batch_outputs'],
    'workflow item')
wf.set_op_input('sample_realtime','static_input_keys',
    ['integrator',
     'bg_batch_outputs'])




wf = wfmgr.workflows['background_process']

# input 0: path to header file
wf.set_op_input('read_header','file_path',None)
wf.connect_input('header_file','read_header.inputs.file_path')

# input 1: image directory, in case separate from headers
wf.set_op_input('image_path','dir_path',None)
wf.connect_input('image_dir','image_path.inputs.dir_path')

# inputs 2 and 3: q-range for data windowing
# TODO: pass in from batch
wf.set_op_input('q_window','x_min',0.0)
wf.set_op_input('q_window','x_max',1.0)
wf.connect_input('q_min','q_window.inputs.x_min')
wf.connect_input('q_max','q_window.inputs.x_max')

# input 4: key for fetching temperature from header dictionary 
wf.set_op_input('time_temp','temp_key','CTEMP')
wf.connect_input('temp_key','time_temp.inputs.temp_key')

# input 5: pyfai.AzimuthalIntegrator
# AzimthalIntegrators are not serializable,
# so specify this input as 'runtime' type
wf.set_op_input('integrate','integrator',None,'runtime')
wf.connect_input('integrator','integrate.inputs.integrator')

wf.connect_output('temperature','time_temp.outputs.temperature')
wf.connect_output('q_I','integrate.outputs.q_I')
wf.connect_output('q_I_dz','dezinger.outputs.q_I_dz')
wf.connect_output('q_logI_dz','log_I.outputs.x_logy')

wf.set_op_input('image_path','filename','read_header.outputs.filename','workflow item')
wf.set_op_input('image_path','ext','tif')
wf.set_op_input('read_image','file_path','image_path.outputs.file_path','workflow item')
wf.set_op_input('time_temp','header_dict','read_header.outputs.header_dict','workflow item')
wf.set_op_input('time_temp','time_key','time')
wf.set_op_input('integrate','image_data','read_image.outputs.image_data','workflow item')
wf.set_op_input('q_window','x_y','integrate.outputs.q_I','workflow item')
wf.set_op_input('dezinger','q_I','q_window.outputs.x_y_window','workflow item')
wf.set_op_input('log_I','x_y','dezinger.outputs.q_I_dz','workflow item')
wf.set_op_input('output_CSV','array','dezinger.outputs.q_I_dz','workflow item')
wf.set_op_input('output_CSV','headers',['q (1/angstrom)','intensity (arb)'])
wf.set_op_input('output_CSV','dir_path','read_header.outputs.dir_path','workflow item')
wf.set_op_input('output_CSV','filename','read_header.outputs.filename','workflow item')
wf.set_op_input('output_CSV','filetag','_dz')


wf = wfmgr.workflows['sample_process']

# input 0: path to header file
wf.set_op_input('read_header','file_path',None)
wf.connect_input('header_file','read_header.inputs.file_path')

# input 1: image directory, in case separate from headers
wf.set_op_input('image_path','dir_path',None)
wf.connect_input('image_dir','image_path.inputs.dir_path')

# inputs 2 and 3: q-range for data windowing
# TODO: pass in from batch
wf.set_op_input('q_window','x_min',0.0)
wf.set_op_input('q_window','x_max',1.0)
wf.connect_input('q_min','q_window.inputs.x_min')
wf.connect_input('q_max','q_window.inputs.x_max')

# input 4: key for fetching temperature from header dictionary 
wf.set_op_input('time_temp','temp_key','CTEMP')
wf.connect_input('temp_key','time_temp.inputs.temp_key')

# input 5: pyfai.AzimuthalIntegrator
# AzimthalIntegrators are not serializable,
# so specify this input as 'runtime' type
wf.set_op_input('integrate','integrator',None,'runtime')
wf.connect_input('integrator','integrate.inputs.integrator')

# input 6: the outputs of the background batch 
wf.connect_input('bg_batch_outputs','bg_subtract.inputs.bg_batch_outputs')
wf.set_op_input('bg_subtract','bg_batch_outputs',None)

wf.connect_output('time','time_temp.outputs.time')
wf.connect_output('temperature','time_temp.outputs.temperature')
wf.connect_output('q_I','integrate.outputs.q_I')
wf.connect_output('q_I_dz','dezinger.outputs.q_I_dz')
wf.connect_output('q_I_dz_bgsub','bg_subtract.outputs.q_I_bgsub')
wf.connect_output('q_logI_dz_bgsub','logI.outputs.x_logy')

wf.set_op_input('image_path','filename','read_header.outputs.filename','workflow item')
wf.set_op_input('image_path','ext','tif')
wf.set_op_input('read_image','file_path','image_path.outputs.file_path','workflow item')
wf.set_op_input('time_temp','header_dict','read_header.outputs.header_dict','workflow item')
wf.set_op_input('time_temp','time_key','time')
wf.set_op_input('integrate','image_data','read_image.outputs.image_data','workflow item')
wf.set_op_input('q_window','x_y','integrate.outputs.q_I','workflow item')
wf.set_op_input('dezinger','q_I','q_window.outputs.x_y_window','workflow item')
wf.set_op_input('bg_subtract','q_I_meas','dezinger.outputs.q_I_dz','workflow item')
wf.set_op_input('bg_subtract','T_meas','time_temp.outputs.temperature','workflow item')
wf.set_op_input('bg_subtract','q_I_bg_key','q_I_dz')
wf.set_op_input('bg_subtract','T_bg_key','temperature')
wf.set_op_input('log_I','x_y','bg_subtract.outputs.q_I_bgsub','workflow item')
wf.set_op_input('output_CSV','array','bg_subtract.outputs.q_I_bgsub','workflow item')
wf.set_op_input('output_CSV','headers',['q (1/angstrom)','intensity (arb)'])
wf.set_op_input('output_CSV','filename','read_image.outputs.filename','workflow item')
wf.set_op_input('output_CSV','filetag','_dz_bgsub')

pawstools.save_to_wfl(os.path.join(pawstools.sourcedir,'core','workflows','SAXS','BL15','realtime_integrate_bgsub.wfl'),wfmgr)


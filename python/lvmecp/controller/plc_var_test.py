#These are fake addresses to test the code
#Read only plc variables 
plc_var_list = dict()
plc_var_list['Local_control'] = [0x01, 225]  # Shows if local control is activated or not (0 for TCS control)

#Define Dome variables
plc_var_list['Dome_act_pos'] = [0x03, 1000]  # Actual Dome position (deci-Deg)
plc_var_list['Dome_act_vel'] = [0x03, 1020]  # Actual Dome velocity (deci-Deg/seg)
plc_var_list['Dome_enb_mov'] = [0x01, 200]   # Dome move enable bit
plc_var_list['Dome_in_pos'] =  [0x01, 205]   # Dome in position
plc_var_list['Dome_mot_drf'] = [0x01, 666]   # Dome motors drive fault
plc_var_list['Dome_GS3_ree'] = [0x01, 667]   # GS3 reading error
plc_var_list['Dome_GS3_wre'] = [0x01, 670]   # GS3 writing error
plc_var_list['Dome_GS3_err'] = [0x03, 240]   # GS3 status monitor

#Define windscreen variables
plc_var_list['WS_position'] = [0x03, 310]    # Windscreen position (Lower = 512 | Upper ~ 5375)
plc_var_list['WS_enable'] =   [0x01, 220]    # Windscreen enable bit 

#Define Platform Variables
plc_var_list['plat_not_dwn'] = [0x01, 210]   # Platform not down

#Define shutter variables
plc_var_list['Shut_enable'] = [0x01,240]     # Shutter enable
plc_var_list['Shut_open']   = [0x01,330]     # Shutter open
plc_var_list['Shut_close']  = [0x01,331]     # Shutter close
plc_var_list['Shut_tout']   = [0x01,335]     # Shutter time out error
plc_var_list['Shut_curr']   = [0x03,745]    # Shutter motor current (100 units = 1 A)
plc_var_list['Shut_opning'] = [0x01,344]     # Shutter is opening
plc_var_list['Shut_clsing'] = [0x01,345]     # Shutter is closing

#Define light variables
plc_var_list['Low_lights'] =   [0x01, 336]   # Low light status
plc_var_list['High_lights'] =  [0x01, 337]   # High light status

# Read/Write plc variables
plc_var_talk = dict()

#Define Dome variables
plc_var_talk['Dome_new_pos'] = [0x06, 2000]  # Dome new position (deci-Deg)
plc_var_talk['Dome_enb_mov'] = [0x05, 200]   # Dome move enable bit (Has to go before new pos)

#Define windscreen variables
plc_var_talk['WS_enable'] = [0x05, 220]      # Windscreen enable bit
plc_var_talk['WS_to_top'] = [0x05, 216]      # Windscreen to upper position bit
plc_var_talk['WS_to_btm'] = [0x05, 217]      # Windscreen to lower position bit

#Define Shutter variables
plc_var_talk['Shut_enable'] = [0x05,240]     # Shutter enable
plc_var_talk['Shut_open']   = [0x05,246]     # Shutter open
plc_var_talk['Shut_close']  = [0x05,247]     # Shutter close

#Define light variables
plc_var_talk['Tggl_lights'] =  [0x05,236]    # Light toggle bit
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


#Define light variables
plc_var_list['Low_lights'] =   [0x01, 336]   # Low light status
plc_var_list['High_lights'] =  [0x01, 337]   # High light status

# Read/Write plc variables
plc_var_talk = dict()

#Define Dome variables
plc_var_talk['Dome_new_pos'] = [0x06, 2000]  # Dome new position (deci-Deg)
plc_var_talk['Dome_enb_mov'] = [0x05, 200]   # Dome move enable bit (Has to go before new pos)


#Define light variables
plc_var_talk['Tggl_lights'] =  [0x05,236]    # Light toggle bit
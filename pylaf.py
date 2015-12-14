# +--------------------------------------------------------------------------+
# |   pylaf (flyff tools coded in python) by lava                            |
# |	        created on 10.21.2015(m.d.y) minus 1 week                        |
# |    if you want to donate to lava :                                       |
# |           BTC: 19X7KKkMZsu4dLC3wd93N3UHiDJdomb6Vd                        |
# +__________________________________________________________________________+
# \--------------------------------------------------------------------------/
#  |  This program is free software: you can redistribute it and/or modify  |
#  |  it under the terms of the GNU General Public License as published by  |
#  |  the Free Software Foundation, version 3 of the License                |
#  |                                                                        |
#  |  This program is distributed in the hope that it will be useful,       |
#  |  but WITHOUT ANY WARRANTY; without even the implied warranty of        |
#  |  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         |
#  |  GNU General Public License for more details.                          |
#  |                                                                        |
#  |  You should have received a copy of the GNU General Public License     |
#  |  along with this program.  If not, see <http://www.gnu.org/licenses/>. |
#  +------------------------------------------------------------------------+

try:
	import Tkinter as tk		## Python 2.x
except ImportError :
	import tkinter as tk		## Python 3.x

import array
import os
from os import path
import ctypes
from ctypes import c_long, c_int, c_float, c_uint, c_char, c_ubyte, c_char_p, c_void_p, c_ulong
from ctypes import *
from ctypes.wintypes import *
import struct
import thread
import time
import struct
# https://www.burgaud.com/bring-colors-to-the-windows-console-with-python/
import color_console as cons

proc_id = ctypes.c_ulong()

default_colors = cons.get_text_attr()
default_bg = default_colors & 0x0070

class MODULEENTRY32(ctypes.Structure):
    _fields_ = [ ( 'dwSize' , c_long ) , 
				( 'th32ModuleID' , c_long ),
				( 'th32ProcessID' , c_long ),
				( 'GlblcntUsage' , c_long ),
				( 'ProccntUsage' , c_long ) ,
				( 'modBaseAddr' , c_long ) ,
				( 'modBaseSize' , c_long ) , 
				( 'hModule' , c_void_p ) ,
				( 'szModule' , c_char * 256 ),
				( 'szExePath' , c_char * 260 ) ]

def is_pylaf_conf(filename) :
	file_extension = filename.split('.')
	if (file_extension[len(file_extension) -1] == "pylaf") :
		return True
		
def is_hex(s):
    hex_digits = set("0123456789abcdef")
    for char in s:
        if not (char in hex_digits):
            return False
    return True

def write_memory(proc_handle, address, data, type):
	count = c_ulong(0)
	
	if (type == "int") :
		int_arr = [0, 0, 0, 0]
		int_arr[0] = (data >> 24) & 0xff
		int_arr[1] = (data >> 16) & 0xff
		int_arr[2] = (data >> 8) & 0xff
		int_arr[3] = data & 0xff
		
		by_str = ""
		for i in range(4) :
			s_str = hex(int_arr[3 -i]).split("x")[1]
			
			if (len(s_str) != 2) :
				s_str = "0" + s_str
				
			by_str += s_str
		
		data_to_use = by_str.decode("hex")
	else :
		data_to_use = data
	
	length = len(data_to_use)
	c_data = c_char_p(data_to_use[count.value:])
	
	old_protect = c_ulong(0)
	ctypes.windll.kernel32.VirtualProtectEx(proc_handle, address, 256, 0x40, ctypes.byref(old_protect))
	
	if not ctypes.windll.kernel32.WriteProcessMemory(proc_handle, address, c_data, length, ctypes.byref(count)):
		print ("Failed: Write Memory - Error Code: ", ctypes.windll.kernel32.GetLastError())
		print (hex(address) + " " + str(c_data))
		ctypes.windll.kernel32.SetLastError(10000)
	else:
		ctypes.windll.kernel32.VirtualProtectEx(proc_handle, address, 256, old_protect, 0)
		return False
		
# nice: http://stackoverflow.com/questions/19684697/python-converting-byte-address-from-readprocessmemory-to-string
def read_memory(proc_handle, address, size, debug_it, type):
	buffer = c_char_p(b"The data goes here")
	
	if (type == "float") :
		val = c_float();
	else :
		val = c_int()
		
	bytesRead = c_ulong(0)

	if ctypes.windll.kernel32.ReadProcessMemory(proc_handle, address, buffer, size, ctypes.byref(bytesRead)):
		memmove(ctypes.byref(val), buffer, ctypes.sizeof(val))
		
		if (debug_it == True) :
			print("Success reading: " + hex(address) + " value: " + str(val.value))
			
		return str(val.value)
	else:
		if (debug_it == True) :
			print("Failed.")
			
		return None

# http://code.activestate.com/recipes/576362-list-system-process-and-process-information-on-win/
def get_module(pid, module_name):
	hSnapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot(0x00000008, pid)
	me32 = MODULEENTRY32()
	me32.dwSize = ctypes.sizeof(MODULEENTRY32)
	
	while (ctypes.windll.kernel32.Module32Next(hSnapshot, ctypes.pointer(me32)) == True) :
		print("    >nextmodule: %s" % me32.szModule)
		
		if (me32.szModule == module_name) :
			return me32.modBaseAddr
				
	return ""

def is_float(num) :
	try :
		float(num)
		return True
	except ValueError:
		return False

def isNumber(num) :
	numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", ","]
	for number in numbers :
		if number == num :
			return True
	return False
		
def get_write_sum(line, integers, floating_points) :
	marks = ["*", "/", "+", "-"]
	
	if "+" in line or "-" in line or "*" in line or "/" in line :
		_sum_ = 0
		
		for mark in marks :
			while mark in line :
				readingFirst = True
				_adds_ = ["", ""]
				end = 0
				
				for i in range(len(line)) :
					if line[i] not in marks :
						if readingFirst == True :
							_adds_[0] += line[i]
						else :
							_adds_[1] += line[i]
					elif line[i] == mark :
						if readingFirst == False :
							end = i
							break
							
						readingFirst = False
					else :
						if readingFirst == False :
							end = i
							break
							
						_adds_[0] = ""
				
				if mark == "*" or mark == "/" : 
					_sum_ = 1
				else :
					_sum_ = 0
					
				for _add_ in _adds_ :
					if (_add_.endswith("i") and _add_[:len(_add_) -1].isdigit()) :
						if mark == "+" :
							_sum_ += int(_add_[:len(_add_) -1], 10)
						elif mark == "-" :
							_sum_ -= int(_add_[:len(_add_) -1], 10)
						elif mark == "*" :
							_sum_ *= int(_add_[:len(_add_) -1], 10)
						elif mark == "/" :
							_sum_ /= int(_add_[:len(_add_) -1], 10)
					elif (_add_.endswith("f") and is_float(_add_[:len(_add_) -1])) :
						if mark == "+" :
							_sum_ += float(_add_[:len(_add_) -1])
						elif mark == "-" :
							_sum_ -= float(_add_[:len(_add_) -1])
						elif mark == "*" :
							_sum_ *= float(_add_[:len(_add_) -1])
						elif mark == "/" :
							_sum_ /= float(_add_[:len(_add_) -1])
					elif (is_hex(_add_.lower()) == True) :
						if mark == "+" :
							_sum_ += int(_add_, 16)
						elif mark == "-" :
							_sum_ -= int(_add_, 16)
						elif mark == "*" :
							_sum_ *= int(_add_, 16)
						elif mark == "/" :
							_sum_ /= int(_add_, 16)
					else :
						for variable in integers :
							exploded = variable.split("=")
							if (_add_ == exploded[0]) :
								if mark == "+" :
									_sum_ += int(exploded[1], 10)
								elif mark == "-" :
									_sum_ -= int(exploded[1], 10)
								elif mark == "*" :
									_sum_ *= int(exploded[1], 10)
								elif mark == "/" :
									_sum_ /= int(exploded[1], 10)
								
								break
								
						for variable in floating_points :
							exploded = variable.split("=")
							if (_add_ == exploded[0]) :
								if mark == "+" :
									_sum_ += float(exploded[1])
								elif mark == "-" :
									_sum_ -= float(exploded[1])
								elif mark == "*" :
									_sum_ *= float(exploded[1])
								elif mark == "/" :
									_sum_ /= float(exploded[1])
									
								break
				
				if end == 0 :
					line = line[:len(line) - (len(_adds_[0]) + len(_adds_[1]))]
				else :
					line = line[:end - (len(_adds_[0]) + len(_adds_[1]) +1)] + hex(_sum_).split("x")[1] + line[end:]
		
		return _sum_
	else :
		if (line.endswith("i") and line[:len(line) -1].isdigit()) :
			return int(line[:len(line) -1], 10)
		elif (line.endswith("f") and is_float(line[:len(line) -1])) :
			return float(line[:len(line) -1])
		elif (is_hex(line.lower()) == True) :
			return int(line, 16)
		else :
			for variable in integers :
				exploded = variable.split("=")
				if (line == exploded[0]) :
					return int(exploded[1], 10)
					
			for variable in floating_points :
				exploded = variable.split("=")
				if (line == exploded[0]) :
					return float(exploded[1])
		
def get_pointed_sum(line, proc_handle, integers, floating_points, debug_it, type) :
	points = line.split(">")
	
	_sum_ = 0
	
	i = 0
	for point in points :
		if (i == len(points) -1) :
			_sum_ += get_write_sum(point, integers, floating_points)
		else :
			if (type == "float") :
				if (i == len(points) -2) :
					_sum_ = float(read_memory(proc_handle, _sum_ + get_write_sum(point, integers, floating_points), 4, debug_it, "float"))
				else :
					_sum_ = int(read_memory(proc_handle, _sum_ + get_write_sum(point, integers, floating_points), 4, debug_it, "int"), 10)
			else :
				_sum_ = int(read_memory(proc_handle, _sum_ + get_write_sum(point, integers, floating_points), 4, debug_it, "int"), 10)
			
		i += 1
		
	return _sum_

def parse_line(proc_handle, line, line_num, debug_it) :
	bad_line = False
	global default_bg
	global default_colors
	
	if (debug_it == True) :
		cons.set_text_attr(default_colors)
	
	if (line.startswith("int:")) :
		set_variable(line, proc_handle, debug_it, "int")
	elif (line.startswith("float:")) :
		set_variable(line, proc_handle, debug_it, "float")
	elif (line.startswith("write:") or line.startswith("write.")) :
		set_write(line, proc_handle, debug_it)
	elif (line.startswith("sleep:")) :
		timeToSleep = int(line.split(":")[1])
		time.sleep(timeToSleep / 1000.0)
	elif (line.startswith("print:")) :
		print(line[6:])
	elif (line.startswith("print.var:")) :
		print(get_sum(line[10:], proc_handle, integers, floating_points, debug_it))
	elif (line != "") :
		bad_line = True
		
		if (debug_it == True) :
			cons.set_text_attr(cons.FOREGROUND_RED | default_bg | cons.FOREGROUND_INTENSITY)
			
	if (bad_line == False) :
		if (debug_it == True) :
			cons.set_text_attr(cons.FOREGROUND_GREEN | default_bg | cons.FOREGROUND_INTENSITY)
	
	if (debug_it == True) :
		print(str(line_num) + ":     " + line)
		cons.set_text_attr(default_colors)
		
	if (bad_line == True) :
		return False
	else :
		return True

def parse_gui(frame, line, line_num, debug_it) :
	if (line.startswith("gui.label:")) :
		tk.Label(frame, text=line[10:]).pack(side="left")
		debugGreen("drawing label with text: " + line[10:])


range_lines_ON = []
range_lines_OFF = []

def set_range(proc_handle, bo_state) :
	if (bo_state == True) :
		global range_lines_ON
		lines = range_lines_ON
	else :
		global range_lines_OFF
		lines = range_lines_OFF
	
	line_num = 1
	
	global default_bg
	global default_colors
	
	for line in lines :	
		parse_line(proc_handle, line, line_num, True)
		
		line_num += 1
	
	print("end of range action")

selected_spam_bytes = []
spam_bytes_arr = []

def onselect(evt) :
	global selected_spam_bytes
	priv_selected_spam_bytes = []
	
	selected_arr = evt.widget.curselection()
	
	for index in range(len(selected_arr)) :
		index = int(evt.widget.curselection()[index])
		print ("selected item " + evt.widget.get(index) + ", byte " + spam_bytes_arr[index])
		priv_selected_spam_bytes.append(spam_bytes_arr[index])
		
	selected_spam_bytes = priv_selected_spam_bytes
	print("end of selected ones")
	
using_spam_thread = False
kill_spam_thread = False
sleeptime = 100.0

def _spam_thread(hwnd) :
	global using_spam_thread
	global kill_spam_thread
	global selected_spam_bytes
	
	#print ("made key spammer thread")
	
	while True :
		if (kill_spam_thread == True) :
			break
			
		if (using_spam_thread == True) :
			for spam_bye in selected_spam_bytes :
				ctypes.windll.user32.PostMessageA(hwnd, 0x0100, int(str(spam_bye), 16), 0x001C0001)
		
		time.sleep(sleeptime / 1000)
	
	return
	
def set_thread(bo_state) :
	global using_spam_thread
	
	if (bo_state == True) :
		using_spam_thread = True
	else :
		using_spam_thread = False
		
	print ("set thread " + str(using_spam_thread))
	
integers = []
floating_points = []

def set_variable(line, proc_handle, debug_it, type) :
	global integers
	global floating_points
	
	if (type == "float") :
		__sum = 0.0
	else :
		__sum = 0
	
	got_var = line.split("=")[1]
	if ":" in got_var :
		got_var = got_var.split(":")
		
		for index in range(len(got_var) -1) :
			i = len(got_var) - index -1
			                                                   
			if (got_var[i -1] == "read") :
				_sum = read_memory(proc_handle, get_sum(got_var[i], proc_handle, integers, floating_points, debug_it), 4, debug_it, type)
				
				if (type == "float") :
					__sum += float(_sum)
				else :
					__sum += int(_sum)
			elif (got_var[i -1] == "module") :
				if (is_hex(got_var[i].lower()) == True) :
					if (debug_it == True) :
						print("    >got module baseaddr [%s]" % got_var[i]);
					
					__sum = int(got_var[i], 16)
				else :
					if (debug_it == True) :
						print("    >got module name [%s]" % got_var[i]);
					
					global proc_id
					module = get_module(proc_id, got_var[i])
					
					if (module != "") :
						if (debug_it == True) :
							print("    >got module address [%s]" % hex(module));
						
						__sum = int(module)
					else :
						if (debug_it == True) :
							print("    >no module found")
							
						ctypes.windll.user32.MessageBoxA(0, "module not found\ngoing to exit program", "cancer 404", 0)
						
						exit_me()
			elif (got_var[i -1] == "GetAsyncKeyState") :
				__sum = ctypes.windll.user32.GetAsyncKeyState(ord(got_var[i].decode("hex")))
			else :				
				__sum += get_sum(got_var[i], proc_handle, integers, floating_points, debug_it, type)
			# end of if got var gots some function to use
		# end of for loop
	else :
		__sum += get_sum(got_var, proc_handle, integers, floating_points, debug_it, type)
	
		
	var_name = line.split(":")[1].split("=")[0]
	if (debug_it == True) :
		if (type == "float") :
			print("    >float " + var_name + " = " + str(__sum))
		else:
			print("    >integer " + var_name + " = " + hex(__sum))
	
	does_variable_exists = False
	if (type == "float") :
		for index in range(len(floating_points)) :
			if (floating_points[index].split("=")[0] == var_name) :
				floating_points[index] = var_name + "=" + str(__sum)
				does_variable_exists = True
				break
		
		if (does_variable_exists == False) :
			floating_points.append(var_name + "=" + str(__sum))

	else :
		for index in range(len(integers)) :
			if (integers[index].split("=")[0] == var_name) :
				integers[index] = var_name + "=" + str(__sum)
				does_variable_exists = True
				break
		
		if (does_variable_exists == False) :
			integers.append(var_name + "=" + str(__sum))
		
def set_write(line, proc_handle, debug_it) :
	global integers
	
	if (line.startswith("write:")) :
		new_line = line.split(":")[1].split(",")
		_sum = get_sum(new_line[0], proc_handle, integers, floating_points, debug_it)
		
		# writing bytes
		if not write_memory(proc_handle, _sum, new_line[1].decode("hex"), None) :
			print("wrote bytes: " + new_line[1] + " to " + hex(_sum))
	elif (line.startswith("write.dword:")) :
		new_line = line.split(":")[1].split(",")
		
		exploded = get_sum(new_line[1], proc_handle, integers, floating_points, debug_it)
		hex_data = hex(exploded).split("x")[1]
		while len(hex_data) < 8 :
			hex_data = "0" + hex_data[0:];
			
		new_hex_data = ""
		arr_len = len(hex_data) -1
		
		for index in range(len(hex_data) /2) :
			new_hex_data += hex_data[arr_len - (index *2) -1] + hex_data[arr_len - (index *2)]
					
		if (is_hex(new_hex_data) == True) :
			_sum = get_sum(new_line[0], proc_handle, integers, floating_points, debug_it)
			
			# writing bytes
			if not write_memory(proc_handle, _sum, new_hex_data.decode("hex"), None) :
				if (debug_it == True) :
					print("wrote bytes: " + new_hex_data + " to " + hex(_sum))
		else :
			if (debug_it == True) :
				
				print("    >" + str(new_line[1]) + " is not digit")
	elif (line.startswith("write.int:")) :
		new_line = line.split(":")[1].split(",")
		
		_sum = get_sum(new_line[0], proc_handle, integers, floating_points, debug_it)
		_sum_to_write = get_sum(new_line[1], proc_handle, integers, floating_points, debug_it)
		
		# writing int
		if not write_memory(proc_handle, _sum, _sum_to_write, "int") :
			if (debug_it == True) :
				print("wrote bytes: " + new_line[1] + " to " + hex(_sum))
	elif (line.startswith("write.float:")) :
		new_line = line.split(":")[1].split(",")
		
		_sum = get_sum(new_line[0], proc_handle, integers, floating_points, debug_it)
		_sum_to_write = get_sum(new_line[1], proc_handle, integers, floating_points, debug_it, "float")
		
		# writing bytes
		if not write_memory(proc_handle, _sum, struct.pack('f', _sum_to_write), None) :
			if (debug_it == True) :
				print("wrote float: " + new_line[1] + " to " + hex(_sum))

def get_sum(line, proc_handle, integers, floating_points, debug_it, type = "int") :
	if ">" in line :
		_sum = get_pointed_sum(line, proc_handle, integers, floating_points, debug_it, type)
	elif "(f)>" in line :
		_sum = get_pointed_sum(line, proc_handle, integers, floating_points, debug_it, "float")
	else :
		_sum = get_write_sum(line, integers, floating_points)
	
	return _sum

def is_one_if_true(line, proc_handle, integers, floating_points, debug_it) :
	if "!=" in line :
		compare = line.split("!=")
		
		_sum = get_sum(compare[0], proc_handle, integers, floating_points, debug_it)
		_sum2 = get_sum(compare[1], proc_handle, integers, floating_points, debug_it)
		
		if (_sum != _sum2) :
			return True
		else :
			return False
	elif "==" in line :
		compare = line.split("==")
		
		_sum = get_sum(compare[0], proc_handle, integers, floating_points, debug_it)
		_sum2 = get_sum(compare[1], proc_handle, integers, floating_points, debug_it)
		
		if (_sum == _sum2) :
			return True
		else :
			return False
	elif "<<" in line :
		compare = line.split("<<")
		
		_sum = get_sum(compare[0], proc_handle, integers, floating_points, debug_it)
		_sum2 = get_sum(compare[1], proc_handle, integers, floating_points, debug_it)
		
		if (_sum < _sum2) :
			return True
		else :
			return False
	elif ">>" in line :
		compare = line.split(">>")
		
		_sum = get_sum(compare[0], proc_handle, integers, floating_points, debug_it)
		_sum2 = get_sum(compare[1], proc_handle, integers, floating_points, debug_it)
		
		if (_sum > _sum2) :
			return True
		else :
			return False
	else :
		return False

def is_if_true(line, proc_handle, integers, floating_points, debug_it) :
	if ":" in line :
		# some function has been found in if sentence
		
		funcs = line.split(":")
		is_it_true = False
		
		for index in range(len(funcs)) :
			if (funcs[index -1].endswith("or")) :
				if (funcs[index].endswith("or") or funcs[index].endswith("and")) :
					funcs[index] = funcs[index][:len(funcs[index]) -1]
				
				if is_it_true or is_one_if_true(funcs[index], proc_handle, integers, floating_points, debug_it) :
					is_it_true = True
				else :
					is_it_true = False
			elif (funcs[index -1].endswith("&")) :
				if (funcs[index].endswith("or") or funcs[index].endswith("and")) :
					funcs[index] = funcs[index][:len(funcs[index]) -1]
					
				if is_it_true and is_one_if_true(funcs[index], proc_handle, integers, floating_points, debug_it) :
					is_it_true = True
				else :
					is_it_true = False
			else :
				if (funcs[index].endswith("or") or funcs[index].endswith("and")) :
					funcs[index] = funcs[index][:len(funcs[index]) -1]
				
				is_it_true = is_one_if_true(funcs[index], proc_handle, integers, floating_points, debug_it)
				
		return is_it_true
	else :
		return is_one_if_true(line, proc_handle, integers, floating_points, debug_it)
	

def add_to_select_lines(line, bo_state) :
	if (bo_state == True) :
		global auto_select_lines_ON
		if (line != "") :
			auto_select_lines_ON.append(line)
	else :
		global auto_select_lines_OFF
		if (line != "") :
			auto_select_lines_OFF.append(line)

def add_to_range_lines(line, bo_state) :
	if (bo_state == True) :
		global range_lines_ON
		if (line != "") :
			range_lines_ON.append(line)
	else :
		global range_lines_OFF
		if (line != "") :
			range_lines_OFF.append(line)

def add_to_teleport_lines(line) :
	global teleport_thread_lines
	if (line != "") :
		teleport_thread_lines.append(line)

def check_once(lines, proc_handle) :
	debug_it = True
	
	readingOnce = False
	once_starts = 0
	
	line_num = 0
	for line in lines :
		line = line.strip()
		
		if (readingOnce == True) :
			if (line.startswith("debug=")) :
				boolean = line.split("=")[1]
				
				if (boolean == "0" or boolean == "false") :
					print("    >debug has been set to false")
					debug_it = False
				elif (boolean == "1" or boolean == "true") :
					print("    >debug has been set to true")
					debug_it = True
				else :
					cons.set_text_attr(cons.FOREGROUND_RED | default_bg | cons.FOREGROUND_INTENSITY)
					print(line + " <- bad command")
					cons.set_text_attr(default_colors)
			elif (line == "}") :
				readingOnce = False
				lines = lines[:once_starts] + lines[line_num +1:]
				break
			else :
				parse_line(proc_handle, line, line_num, debug_it)
		elif (line.startswith("once={")) :
			readingOnce = True
			once_starts = line_num
			
		line_num += 1
			
	return (lines, debug_it)

def check_if(line, line_num, proc_handle, is_if_true_arr, if_clauses, debug_it) :
	global integers
	global floating_points
	
	global default_bg
	global default_colors
	
	if (is_if_true_arr[if_clauses] == True) :
		if (line.startswith("if:")) :
			new_line = line[3:]
			
			if (is_if_true(new_line, proc_handle, integers, floating_points, debug_it) == True) :
				is_if_true_arr.append(True)
				
				if (debug_it == True) :
					print("    >if sentence is true")
			else :
				is_if_true_arr.append(False)
				
				if (debug_it == True) :
					print("    >if sentence is false")
			
			if_clauses += 1
			
			if (debug_it == True) :
				cons.set_text_attr(cons.FOREGROUND_GREEN | default_bg | cons.FOREGROUND_INTENSITY)
				print(str(line_num) + ":     " + line)
				cons.set_text_attr(default_colors)
		elif (line == "else") :
			is_if_true_arr[if_clauses] = False
			
			if (debug_it == True) :
				print ("    >if sentence was true so need for else")
				cons.set_text_attr(cons.FOREGROUND_GREEN | default_bg | cons.FOREGROUND_INTENSITY)
				print(str(line_num) + ":     " + line)
				cons.set_text_attr(default_colors)
		elif (line == "endif") :
			is_if_true_arr = is_if_true_arr[:if_clauses]
			if_clauses -= 1
			
			if (debug_it == True) :
				print ("    >true if sentence end")
				cons.set_text_attr(cons.FOREGROUND_GREEN | default_bg | cons.FOREGROUND_INTENSITY)
				print(str(line_num) + ":     " + line)
				cons.set_text_attr(default_colors)
		else :
			parse_line(proc_handle, line, line_num, debug_it)
	else :
		if (line == "else") :
			if (is_if_true_arr[if_clauses -1] == True) :
				is_if_true_arr[if_clauses] = True
			
				if (debug_it == True) :
					print ("    >if sentence was false so going to check else")
					cons.set_text_attr(cons.FOREGROUND_GREEN | default_bg | cons.FOREGROUND_INTENSITY)
					print(str(line_num) + ":     " + line)
					cons.set_text_attr(default_colors)
		elif (line == "endif") :
			is_if_true_arr = is_if_true_arr[:if_clauses]
			if_clauses -= 1
			
			if (debug_it == True) :
				print ("    >false if sentence end")
				cons.set_text_attr(cons.FOREGROUND_GREEN | default_bg | cons.FOREGROUND_INTENSITY)
				print(str(line_num) + ":     " + line)
				cons.set_text_attr(default_colors)
		elif (line.startswith("if:")) :
			is_if_true_arr.append(False)
			if_clauses += 1
			
	return (if_clauses, is_if_true_arr)

using_teleport_thread = False
kill_teleport_thread = False
teleport_thread_sleep_time = 100.0
teleport_thread_lines = []

def _teleport_thread(proc_handle) :
	global using_teleport_thread
	global kill_teleport_thread
	global teleport_thread_sleep_time
	global teleport_thread_lines
	
	v_teleport_thread_lines = teleport_thread_lines
	checked_once = False
	debug_it = True
	stateWas = False
	
	if_clauses = 0
	is_if_true_arr = [True]
	
	while True :
		if (kill_teleport_thread == True) :
			break
			
		if (using_teleport_thread == True) :
			if (stateWas == False) :
				stateWas = True
				checked_once = False
				v_teleport_thread_lines = teleport_thread_lines
			
			line_num = 0
			for line in v_teleport_thread_lines :
				line = line.strip()
				
				if (checked_once == False):
					v_teleport_thread_lines, debug_it = check_once(v_teleport_thread_lines, proc_handle)
					checked_once = True
				
				if_clauses, is_if_true_arr = check_if(line, line_num, proc_handle, is_if_true_arr, if_clauses, debug_it)
				
				line_num += 1
		else:
			if (stateWas == True) :
				stateWas = False
				checked_once = False
				
		time.sleep(teleport_thread_sleep_time / 1000)
	
	return

using_select_thread = False
kill_select_thread = False
select_thread_sleep_time = 100.0
auto_select_lines_ON = []
auto_select_lines_OFF = []

def _select_thread(proc_handle) :
	global using_select_thread
	global kill_select_thread
	global select_thread_sleep_time
	global auto_select_lines_ON
	global auto_select_lines_OFF
	
	v_auto_select_lines = ""
	checked_once = False
	debug_it = True
	stateWas = False
	
	if_clauses = 0
	is_if_true_arr = [True]
	
	while True :
		if (kill_select_thread == True) :
			break;
			
		if (using_select_thread == True) :
			if (stateWas == False) :
				stateWas = True
				checked_once = False
				v_auto_select_lines = auto_select_lines_ON
		else :
			if (stateWas == True) :
				stateWas = False
				checked_once = False
				v_auto_select_lines = auto_select_lines_OFF
				
		line_num = 0
		for line in v_auto_select_lines :
			line = line.strip()
			
			if (checked_once == False) :
				v_auto_select_lines, debug_it = check_once(v_auto_select_lines, proc_handle)
				checked_once = True	
				
			if_clauses, is_if_true_arr = check_if(line, line_num, proc_handle, is_if_true_arr, if_clauses, debug_it)
			
			line_num += 1
				
		time.sleep(select_thread_sleep_time / 1000)
	
	return

def set_select_thread(bo_state) :
	global using_select_thread
	using_select_thread = bo_state

def set_telport_thread(bo_state) :
	global using_teleport_thread
	using_teleport_thread = bo_state
	
customFunctionProp = []

def addCustomFunctionProp(name) :
	global customFunctionProp
	customFunctionProp.append([name, [], []])
	
def fillCustomFunctionProp(name, prop, value) :
	global customFunctionProp
	for i in range(len(customFunctionProp)) :
		if (customFunctionProp[i][0] == name) :
			if (prop == "ON") :
				customFunctionProp[i][1].append(value)
			elif (prop == "OFF") :
				customFunctionProp[i][2].append(value)

def runCustomFunction(name, prop, proc_handle) :
	global customFunctionProp
	v_auto_select_lines = ""
	
	if_clauses = 0
	is_if_true_arr = [True]
	
	for i in range(len(customFunctionProp)) :
		if (customFunctionProp[i][0] == name) :
			if (prop == "ON") :
				v_auto_select_lines = customFunctionProp[i][1]
			elif (prop == "OFF") :
				v_auto_select_lines = customFunctionProp[i][2]
				
			line_num = 0
			for line in v_auto_select_lines :					
				if_clauses, is_if_true_arr = check_if(line, line_num, proc_handle, is_if_true_arr, if_clauses, True)
				
				line_num += 1

def exit_me() :
	global kill_spam_thread
	global kill_select_thread
	global kill_teleport_thread
	
	kill_spam_thread = True
	kill_select_thread = True
	kill_teleport_thread = True
	
	print ("bye bye")
	exit()

def on_closing() :
	exit_me()
	
def debugGreen(msg) :
	global default_bg
	global default_colors
	
	cons.set_text_attr(default_colors)
	print("    >" + msg)
	cons.set_text_attr(cons.FOREGROUND_GREEN | default_bg | cons.FOREGROUND_INTENSITY)

def choice_conf(filename) :
	print("clicked: %s" % filename)
	window.destroy()
	
	newwin = tk.Tk()
	newwin.title("pylaf (flyff tools coded in python) by lava")
	newwin.resizable(width="false", height="false")
	newwin.minsize(380, 200);
	newwin.protocol("WM_DELETE_WINDOW", on_closing)
	
	readingRange = False
	readingRagneON = False
	readingRagneOFF = False
	
	readingSpamSkill = False
	readingSpamSkillOptions = False
	readingSpamSkillOptionsIndex = 0;
	
	readingAutoSelectTarget = False
	readingAutoSelectTargetON = False
	readingAutoSelectTargetOFF = False
	waigin_for_end = False
	
	readingMouseClickTeleport = False
	readingMouseClickTeleportON = False
	
	readingCustomOption = False
	readingCustomOptionON = False
	readingCustomOptionOFF = False
	customFunctionName = ""
	
	global integers
	
	module = 0
	proc_handle = 0
	
	global proc_id
	
	bad_lines_count = 0
	
	global default_bg
	global default_colors
	
	line_num = 1
	with open(filename) as f :
		for line in f :
			line = line.strip()
			
			bad_line = False
			dont_color = False
			used_parse = False
			
			inquotes = False
			index = 0
			
			for char in line :			
				if (inquotes == True) :
					if (char == '"') :
						inquotes = False
						line = line[:index] + line[index +1:]
					else :
						index += 1
				elif (char == '"') :
					inquotes = True
					line = line[:index] + line[index +1:]
				elif (char == ' ') :
					line = line[:index] + line[index +1:]
				elif (char == '	') :
					line = line[:index] + line[index +1:]
				else :
					index += 1
					
				if (char == ';') :
					exploded = line.split(";")
					print("    >not reading comment:\n" + line[index:])
					line = exploded[0]
					
			if (len(line) > 1) :
				if (line[len(line) -1] == "\"") :
					line = line[:len(line) -1]
					
			if len(line) != 0 :
				cons.set_text_attr(cons.FOREGROUND_GREEN | default_bg | cons.FOREGROUND_INTENSITY)
				
				if (readingRange == True) :
					if (readingRagneON == True) :
						cons.set_text_attr(cons.FOREGROUND_MAGENTA | default_bg | cons.FOREGROUND_INTENSITY)
						dont_color = True
						
						if (waigin_for_end == True) :
							if (line == "}") :
								waigin_for_end = False
								
							add_to_range_lines(line, True)
						elif "{" in line :
							waigin_for_end = True
							add_to_range_lines(line, True)
						elif (line != "}") :
							add_to_range_lines(line, True)
						else :
							cons.set_text_attr(default_colors)
							print("    >end of when range is set to ON")
							readingRagneON = False
							dont_color = False
					elif (readingRagneOFF == True) :
						cons.set_text_attr(cons.FOREGROUND_MAGENTA | default_bg | cons.FOREGROUND_INTENSITY)
						dont_color = True
						
						if (waigin_for_end == True) :
							if (line == "}") :
								waigin_for_end = False
								
							add_to_range_lines(line, False)
						elif "{" in line :
							waigin_for_end = True
							add_to_range_lines(line, False)
						elif (line != "}") :
							add_to_range_lines(line, False)
						else :
							cons.set_text_attr(default_colors)
							print("    >end of when range is set to ON")
							cons.set_text_attr(cons.FOREGROUND_GREEN | default_bg | cons.FOREGROUND_INTENSITY)
							readingRagneOFF = False
							dont_color = False
					elif (line.startswith("ON={")) :
						debugGreen("going to read when range is set to ON")
						readingRagneON = True
						
						# if range ON has defined then drawing its button
						tk.Button(frame, text="range ON", command=lambda :set_range(proc_handle, True)).pack(side="left")
					elif (line.startswith("OFF={")) :
						debugGreen("going to read when range is set to OFF")
						readingRagneOFF = True
						
						# if range OFF has defined then drawing its button
						tk.Button(frame, text="Range OFF", command=lambda :set_range(proc_handle, False)).pack(side="left")
					elif (line == "}") :
						debugGreen("end of range function")
						readingRange = False
						
						# packing range frame
						frame.pack(fill="x")
					elif (line != "") :
						bad_line = True
						bad_lines_count += 1
						
						cons.set_text_attr(cons.FOREGROUND_RED | default_bg | cons.FOREGROUND_INTENSITY)
				elif (readingSpamSkill == True) :
					if (readingSpamSkillOptions == True) :
						if (line == "}") :
							debugGreen("end of options")
							readingSpamSkillOptions = False
							
							# when options reading ended then packing list + scroll bar
							list1.config(width=5, height=3)
							scrollbar.config(command=list1.yview)
							
							list1.pack(side="left")
							scrollbar.pack(side=tk.LEFT, fill=tk.Y)
							
							tk.Button(frame1, text="ON", command=lambda :set_thread(True)).pack(side="left")
							tk.Button(frame1, text="OFF", command=lambda :set_thread(False)).pack(side="left")
						else :
							if "," in line :
								tpb = line.split(',')
								list1.insert(readingSpamSkillOptionsIndex, tpb[0])
								readingSpamSkillOptionsIndex += 1
								
								spam_bytes_arr.append(tpb[1])
					elif (line.startswith("options=")) :
						debugGreen("going to read options")
						readingSpamSkillOptions = True
						tk.Label(frame1, text="spamm skill").pack(side="left")
						
						# making listbox + scroll bar
						scrollbar = tk.Scrollbar(frame1, orient=tk.VERTICAL)
						list1 = tk.Listbox(frame1, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set)
						list1.bind('<<ListboxSelect>>', onselect)
					elif (line.startswith("sleep:")) :
						debugGreen("reading thread sleep time")
						
						global sleeptime
						sleeptime = int(line.split(":")[1]) + 0.0
					elif (line == "}") :
						debugGreen("end of spamSkill function")
						readingSpamSkill = False
						
						# packing spamSkill frame
						frame1.pack(fill="x")
					elif (line != "") :
						bad_line = True
						bad_lines_count += 1
						
						cons.set_text_attr(cons.FOREGROUND_RED | default_bg | cons.FOREGROUND_INTENSITY)
				elif (readingAutoSelectTarget == True) :
					if (readingAutoSelectTargetON == True) :
						cons.set_text_attr(cons.FOREGROUND_MAGENTA | default_bg | cons.FOREGROUND_INTENSITY)
						dont_color = True
						
						if (waigin_for_end == True) :
							if (line == "}") :
								waigin_for_end = False
								
							add_to_select_lines(line, True)
						elif "{" in line :
							waigin_for_end = True
							add_to_select_lines(line, True)
						elif (line != "}") :
							add_to_select_lines(line, True)
						else :
							debugGreen("end of autoSelectTarget when on ON function")
							readingAutoSelectTargetON = False
							dont_color = False
					elif (readingAutoSelectTargetOFF== True) :
						cons.set_text_attr(cons.FOREGROUND_MAGENTA | default_bg | cons.FOREGROUND_INTENSITY)
						dont_color = True
						
						if (waigin_for_end == True) :
							if (line == "}") :
								waigin_for_end = False
								
							add_to_select_lines(line, False)
						elif "{" in line :
							waigin_for_end = True
							add_to_select_lines(line, False)
						elif (line != "}") :
							add_to_select_lines(line, False)
						else :
							debugGreen("end of autoSelectTarget when on OFF function")
							readingAutoSelectTargetOFF = False
							dont_color = False
					elif (line.startswith("sleep:")) :
						debugGreen("reading thread sleep time")
						
						global select_thread_sleep_time
						select_thread_sleep_time = int(line.split(":")[1]) + 0.0
					elif (line.startswith("ON={")) :
						debugGreen("reading autoSelectTarget when on ON function")
						readingAutoSelectTargetON = True
						
						# adding on button
						tk.Button(frame2, text="ON", command=lambda :set_select_thread(True)).pack(side="left")
						tk.Button(frame2, text="OFF", command=lambda :set_select_thread(False)).pack(side="left")
						
						#	making thread
						thread.start_new_thread(_select_thread, (proc_handle,))
					elif (line.startswith("OFF={")) :
						debugGreen("reading autoSelectTarget when on OFF function")
						readingAutoSelectTargetOFF = True
						# thead has been crated when ON exists, so no more ^^
					elif (line == "}") :
						debugGreen("end of autoSelectTarget function")
						readingAutoSelectTarget = False
						
						# packing autoSelectTarget frame
						frame2.pack(fill="x")
					elif (line != "") :
						bad_line = True
						bad_lines_count += 1
						
						cons.set_text_attr(cons.FOREGROUND_RED | default_bg | cons.FOREGROUND_INTENSITY)
				elif (readingMouseClickTeleport == True) :
					if (readingMouseClickTeleportON == True) :
						cons.set_text_attr(cons.FOREGROUND_MAGENTA | default_bg | cons.FOREGROUND_INTENSITY)
						dont_color = True
						
						if (waigin_for_end == True) :
							if (line == "}") :
								waigin_for_end = False
								
							add_to_teleport_lines(line)
						elif "{" in line :
							waigin_for_end = True
							add_to_teleport_lines(line)
						elif (line != "}") :
							add_to_teleport_lines(line)
						else :
							debugGreen("end of mouseClickTeleport function when its on")
							readingMouseClickTeleportON = False
							dont_color = False
					elif (line.startswith("sleep:")) :
						debugGreen("reading thread sleep time")
						
						global teleport_thread_sleep_time
						teleport_thread_sleep_time = int(line.split(":")[1]) + 0.0
					elif (line.startswith("ON={")) :
						debugGreen("going to read when mouseClickTeleport is ON")
						readingMouseClickTeleportON = True
						
						# adding on button
						tk.Button(frame3, text="ON", command=lambda :set_telport_thread(True)).pack(side="left")
						tk.Button(frame3, text="OFF", command=lambda :set_telport_thread(False)).pack(side="left")
						
						#	making thread
						thread.start_new_thread(_teleport_thread, (proc_handle,))
					elif (line == "}") :
						debugGreen("end of mouseClickTeleport function")
						readingMouseClickTeleport = False
						
						# packing mouseClickTeleport frame
						frame3.pack(fill="x")
				elif (readingCustomOption == True) :
					if (readingCustomOptionON == True) :
						cons.set_text_attr(cons.FOREGROUND_MAGENTA | default_bg | cons.FOREGROUND_INTENSITY)
						dont_color = True
						
						if (waigin_for_end == True) :
							if (line == "}") :
								waigin_for_end = False
								
							fillCustomFunctionProp(customFunctionName, "ON", line)
						elif "{" in line :
							waigin_for_end = True
							fillCustomFunctionProp(customFunctionName, "ON", line)
						elif (line != "}") :
							fillCustomFunctionProp(customFunctionName, "ON", line)
						else :
							debugGreen("end of when its ON")
							readingCustomOptionON = False
							dont_color = False
					elif (readingCustomOptionOFF == True) :
						cons.set_text_attr(cons.FOREGROUND_MAGENTA | default_bg | cons.FOREGROUND_INTENSITY)
						dont_color = True
						
						if (waigin_for_end == True) :
							if (line == "}") :
								waigin_for_end = False
								
							fillCustomFunctionProp(customFunctionName, "OFF", line)
						elif "{" in line :
							waigin_for_end = True
							fillCustomFunctionProp(customFunctionName, "OFF", line)
						elif (line != "}") :
							fillCustomFunctionProp(customFunctionName, "OFF", line)
						else :
							debugGreen("end of when its ON")
							readingCustomOptionOFF = False
							dont_color = False
					elif (line.startswith("gui.")):
						parse_gui(frame, line, line_num, True)
					elif (line.startswith("ON={")) :
						debugGreen("going to read when its ON")
						readingCustomOptionON = True
						
						# adding on button
						tk.Button(frame, text="ON", command=lambda :runCustomFunction(customFunctionName, "ON", proc_handle)).pack(side="left")
					elif (line.startswith("OFF={")) :
						debugGreen("going to read when its OFF")
						readingCustomOptionOFF = True
						
						# adding on button
						tk.Button(frame, text="OFF", command=lambda :runCustomFunction(customFunctionName, "OFF", proc_handle)).pack(side="left")
					elif (line == "}") :
						debugGreen("end of custom function")
						readingCustomOption = False
						
						# packing custion function frame
						frame.pack(fill="x")
				elif (line.startswith("window=")) :
					cons.set_text_attr(default_colors)
					# getting window name, it has to be set before write command
					windowName = line.split('=')
					print("    >got window name [%s]" % windowName[1])
					
					hwnd = ctypes.windll.user32.FindWindowA(None, windowName[1])
					print (hwnd)
					
					if (hwnd == 0) :
						print("    >no window found")
						ctypes.windll.user32.MessageBoxA(0, "window not found\ngoing to exit program", "cancer 404", 0)
						
						exit_me()
					else :
						ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(proc_id))
						proc_handle = ctypes.windll.kernel32.OpenProcess(0x38, False, proc_id)
						
						if proc_handle :
							print("    >process opened successfully")
							
							# making key spamming thread
							thread.start_new_thread(_spam_thread, (hwnd,))
						else :
							print("    >there was error while opening process\n    try run it as admin")
							ctypes.windll.user32.MessageBoxA(0, "there was error while opening process\ntry run it as admin", "cancer 404", 0)
							
							exit_me()
				elif (line.startswith("range={")) :
					debugGreen("going to read range function")
					readingRange = True
					
					# creating range frame
					frame = tk.Frame()
				elif (line.startswith("spamSkill={")) :
					debugGreen("going to read spamSkill function")
					readingSpamSkill = True
					
					# creating spamSkill frame
					frame1 = tk.Frame()
				elif (line.startswith("autoSelectTarget={")) :
					debugGreen("going to read autoSelectTarget function")
					readingAutoSelectTarget = True
					
					# creating autoSelectTarget frame
					frame2 = tk.Frame()
					tk.Label(frame2, text="auto select target").pack(side="left")
				elif (line.startswith("mouseClickTeleport={")) :
					debugGreen("going to read mouseClickTeleport function")
					readingMouseClickTeleport = True
					
					# creating mouseClickTeleport frame
					frame3 = tk.Frame()
					tk.Label(frame3, text="mouse click teleport").pack(side="left")
				elif (line.endswith("={")) :
					debugGreen("going to read " + line[:len(line) -2] + " function")
					readingCustomOption = True
					addCustomFunctionProp(line[:len(line) -2])
					customFunctionName = line[:len(line) -2]
					
					# creting custion function frame
					frame = tk.Frame()
				elif (line.startswith("version=")) :
					needs_version = line.split("=")[1]
					if (float(needs_version) > 1.3) :
						print("    >this is not right version for this script")
						ctypes.windll.user32.MessageBoxA(0, "this pylaf is not right version for this scrypt\ngoto youtube.com/c/lavaphox or pylafblue.gdk.mx and check for updates\ngoing to exit program", "cancer 404", 0)
						
						exit_me()
				elif (dont_color == False) :
					if (parse_line(proc_handle, line, line_num, True) == False) :
						bad_lines_count += 1
						
					used_parse = True
				
				if (used_parse == False) :
					print(str(line_num) + ":     " + line)
					
				cons.set_text_attr(default_colors)
			
			line_num += 1
		# enf of reading line by line
	# end of opening file
	
	if (bad_lines_count != 0) :
		cons.set_text_attr(cons.FOREGROUND_RED | default_bg | cons.FOREGROUND_INTENSITY)
		print("bad lines count: " + str(bad_lines_count) + ", scroll up to see red line(s)")
		cons.set_text_attr(default_colors)
	else :
		cons.set_text_attr(cons.FOREGROUND_GREEN | default_bg | cons.FOREGROUND_INTENSITY)
		print("thre is no errors")
		cons.set_text_attr(default_colors)

		
def isUserAdmin():
	if os.name == 'nt':
		# WARNING: requires Windows XP SP2 or higher!
		try:
			return ctypes.windll.shell32.IsUserAnAdmin()
		except:
			traceback.print_exc()
			print "Admin check failed, assuming not an admin."
			return False
	elif os.name == 'posix':
		# Check for root on Posix
		return os.getuid() == 0
	else:
		raise RuntimeError, "Unsupported operating system for this module: %s" % (os.name,)
		
# start of pylaf
if not isUserAdmin() :
	ret = ctypes.windll.user32.MessageBoxA(0, "Do you wish to run it as admin?", "cancer 403", 0x00000004L)
	#if ret ==  0x00000007 :
		# clicked no
	if ret == 0x00000006 :
		# clicked yes
		ctypes.cdll.msvcrt.system("start.bat");
		exit_me()
	
window = tk.Tk()
#window.title("pylaf bot (flyff bot coded in python) by lava")
window.title("select")
window.resizable(width="false", height="false")
window.minsize(200, 300);

directory_path = os.path.dirname(os.path.realpath(__file__))

files = [x for x in os.listdir(directory_path) if path.isfile(directory_path+os.sep+x)]

for file in files:
	if (is_pylaf_conf(file) == True) :
		print("file: %s" % file)
		
		frame = tk.Frame();
		tk.Button(frame, text=file, command=lambda i=file:choice_conf(i)).pack(side="left")
		frame.pack(fill="x")

window.mainloop()
from datetime import datetime
import os
import sys

from stuff import values

def write_log_file(seed, tick, crashed=True):

	path = "{path}\\logs".format(path = sys.path[0])
	current_time = str(datetime.now()).replace(":", "_").split(".")[0]

	#values
	dir_values = dir(values)
	i = 0
	while True:
		if i == len(dir_values):
			break
		if dir_values[i].startswith("__"):
			del dir_values[i]
		else:
			i += 1

	values_str = ""
	for v in dir_values:
		values_str += "\n{attr} = {value}".format(attr = v, value = getattr(values, v))

	file_str = """seed: {seed}\ntick: {tick}\n\nvalues:{values}""".format(
		seed = seed,
		tick = tick,
		values = values_str,
		)

	try:
		os.mkdir(path)
	except:
		pass

	existing_files = os.listdir(path)
	yet_not_reported = True

	for file_name in existing_files:
		with open("{path}\\{file_name}".format(path = path, file_name = file_name), "r") as existing_file:
			existing_file = existing_file.read()
			if existing_file == file_str:
				yet_not_reported = False
				path_to_file = "{path}\\{file_name}".format(path = path, file_name = file_name)
				break

	if yet_not_reported:
		path_to_file = "{path}\\{current_time}.txt".format(path = path, current_time = current_time)
		with open(path_to_file, "w") as file:
			file.write(file_str)
		print("\nCreated a log file\n'{file_name}.txt'\nat location\n'{path}'".format(file_name = current_time, path = path))
	else:
		if crashed:
			that_crash = "That crash"
		else:
			that_crash = "It"
		print("\n{that_crash} is already reported in a log file\n'{file_name}'\nat location\n'{path}'".format(that_crash = that_crash, file_name = file_name, path = path))
	return path_to_file

def send_mail(file, crashed=True):
	if crashed:
		print(("\n\nPlease send us mail to DogsAndSheepsSupp@gmail.com and describe what were you doing before the crash.\n"
				"Please include '{file}' in the crash report.\n"
				"We will inform you about the progress and fix the crash as soon as possible.").format(
	file = file,
	))
	else:
		print("""\n\nPlease send us mail to DogsAndSheepsSupp@gmail.com including
'{file}'""".format(
	file = file,
	))

#For now we are banning that seed on your device, so it will not be randomly picked again.

import runner
import sys
import colorama

colorama.init()


class writer:
	def write(text):
		return sys.stdout.write(colorama.Fore.RED + text + colorama.Fore.RESET)


sys.stderr = writer

try:
	import readline
except ModuleNotFoundError:
	pass

if __name__ == '__main__':
	if sys.argv[1:] != "":
		code = open(sys.argv[1], '')
		runner.main(code, False)
		sys.exit(0)
	var = {}
	while True:
		indent = 0
		i = input('>>> ')
		if i == '.quit':
			break
		i += "\n"
		while True:
			if i.count('(') > i.count(')') or i.count('[') > i.count(']') or i.count('{') > i.count('}'):
				newi = input('... ')
				i += newi + "\n"
				if newi == "":
					break
			else:
				break
		try:
			o, var = runner.main(i, False, var=var)
			if o is not None:
				print(colorama.Fore.CYAN + '<<<' + colorama.Fore.RED, o, '\n' + colorama.Fore.RESET)
		except SystemExit:
			pass

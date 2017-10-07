import os
import subprocess

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

LAUNCH = "solent.demo.snake"

def main():
	venv_python = os.path.join(BASE_DIR, 'venv', 'Scripts', 'python.exe')
	if not os.path.exists(venv_python):
		raise Exception("Assumes venv. (Create venv under the base dir)")
	#
	args = [venv_python, '-B', '-m', LAUNCH]
	print(args)
	subprocess.Popen(
		args=args,
		cwd=BASE_DIR)

if __name__ == '__main__':
	main()

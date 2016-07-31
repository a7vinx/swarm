from setuptools import find_packages
from setuptools import setup

with open('README.md') as f:
	setup(
			name = 'swarm',
			version = '0.5.0',

			author = 'arvin.x',
			author_email = 'arvin.x.ptr@gmail.com',
			description = 'A modular distributed penetration testing tool',
			license = 'GPLv3',
			long_description = f.read(),
			
			packages = find_packages(),
			scripts = ['swarm.py','swarm_s.py'],
			entry_points = {
				'console_scripts': [
					'swarm = swarm:main',
					'swarm-s = swarm_s:main',
					]
				},
			
			install_requires = [
				'pymongo>=3.3.0',
				'beautifulsoup4>=4.5.0',
				'python-libnmap>=0.7.0',
				'requests>=2.7.0',
				'IPy>=0.83',
				'argparse>=1.2.1',
			],
			data_files=[
				('/etc/swarm',['swarm.conf']),
				('/etc/swarm',['etc/dirsc.conf','etc/domainsc.conf','etc/nmap.conf',
					'etc/sitemap.conf','etc/intruder.conf']),
			],
			classifiers = [
				'Programming Language :: Python :: 2.7',
				'Programming Language :: Python :: 2.6',
			],
		)

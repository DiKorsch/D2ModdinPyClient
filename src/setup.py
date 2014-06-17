import os


if os.name == "nt":
    from distutils.core import setup
    import py2exe
    
    setup(name="liftr",
          version="2.3.2",
          author="Dimitri Korsch",
          author_email="korschdima@yahoo.de",
          license="GNU General Public License (GPL)",
          packages=[
                    'd2mp', 
                    'd2mp.ui',
                    'd2mp.core',
                    'd2mp.utils',
                    'd2mp.resources', 
                ],
          package_data={"liftr": ["ui/*", "core/*", "utils/*"]},
          scripts=["main.py"],
          windows=[{"script": "main.py"}],
          options={
             "py2exe": {
                 "includes": ["sip",],
              }
          })
else:
    print("Not implemented yet!")

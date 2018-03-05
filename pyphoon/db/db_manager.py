from os import path, listdir

import datetime
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pyphoon.db.db_tables import BestTrack, Images, Base

class DBManager:
    def __init__(self, db_file):
        self.db_file = db_file
        if not path.exists(db_file):
            try:
                open(db_file, 'w+')
            except OSError as err:
                print("error creating file: " + db_file + ": " + err.strerror)
        self.engine = create_engine('sqlite:///' + db_file)
        Base.metadata.create_all(self.engine)
        session = sessionmaker(bind=self.engine)
        self.besttrack = Base.metadata.tables['besttrack']
        self.session = session()

    def add_besttrack(self, directory):
        files = listdir(directory)
        if self.engine.has_table('besttrack'):
            self.session.query(BestTrack).delete()
        from pyphoon.io.tsv import read_tsv

        for f in files:
            _id = int(path.splitext(f)[0])
            f = path.join(directory, f)
            data = read_tsv(f)
            rows = []
            for line in data:
                entry = BestTrack()
                entry.typ_id = _id
                entry.obs_time = datetime.datetime(int(line[0]), int(line[1]), int(line[2]), int(line[3]))
                entry.typ_class = int(line[4])
                entry.lat = line[5]
                entry.lng = line[6]
                entry.pressure = line[7]
                entry.max_wind = line[8]
                entry.gust = line[9]
                entry.storm_dir = int(line[10])
                entry.storm_rad_maj = int(line[11])
                entry.storm_rad_min = int(line[12])
                entry.gale_dir = int(line[13])
                entry.gale_rad_maj = int(line[14])
                entry.gale_rad_min = int(line[15])
                entry.landfall = int(line[16])
                entry.speed = int(line[17])
                entry.direction = int(line[18])
                entry.interpolated = bool(line[19])
                rows.append(entry)
            self.session.bulk_save_objects(rows)
        self.session.commit()

    def add_images(self, img_path):
        base = declarative_base()
        base.metadata.create_all(self.engine, tables=[Images.__table__])
        session = sessionmaker(bind=self.engine)
        session = session()
        from pyphoon.io.h5 import get_h5_filenames
        files = get_h5_filenames(img_path)

        session.query(Images).delete()
        for file in files[0:5]:
            print(file)

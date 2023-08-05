import os
import logging
from flask import request

log = logging.getLogger('moustache.FileRetriever')
log.setLevel(logging.INFO)


class FileRetriever:
    @staticmethod
    def retrieve(input_file_name, temp_directory):
        if input_file_name not in request.files:
            return False
        f = request.files[input_file_name]
        temp_template_file = os.path.join(temp_directory,f.filename)
        f.save(temp_template_file)
        log.info("Saving template file %s to %s" % (f.filename, temp_template_file))
        return temp_template_file

    @staticmethod
    def retrieve_multiple(input_file_name, temp_directory):
        gabarit_filelist = request.files.getlist(input_file_name)
        gabarit_file_mapping = {}
        log.info("Gabarit file list %s" % gabarit_filelist)

        for gabarit_file in gabarit_filelist:
            temp_gabarit_file = os.path.join(temp_directory, gabarit_file.filename)
            gabarit_file.save(temp_gabarit_file)
            gabarit_file_mapping[gabarit_file.filename] = temp_gabarit_file
            log.info("Saving gabarit %s to %s" % (gabarit_file, temp_gabarit_file))

        return gabarit_file_mapping

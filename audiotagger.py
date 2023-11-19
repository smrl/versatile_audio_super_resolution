import taglib
import json
from pathlib import Path

class AudioTagger:
    """
    A class used to read/write audio file metadata tags.

    Attributes:
        file_path (str): the path to the audio file.
        audio_file (taglib.File): the audio file.
        tags (dict): a dictionary of the audio file's tags.
    """
    def __init__(self, file_path, logger=None):
        self.logger = logger # a BatchLogger
        path = Path(file_path)

        if not path.exists():
            if self.logger:
                self.logger.log_error(f"No such file or directory: {file_path}")
            raise FileNotFoundError(f"No such file or directory: {file_path}")

        if not path.is_file():
            if self.logger:
                self.logger.log_error(f"The path {file_path} is not a file.")
            raise ValueError(f"The path {file_path} is not a file.")

        if path.suffix.lower() != '.wav':
            if self.logger:
                self.logger.log_error(f"The file {file_path} is not a .wav file.")
            raise ValueError(f"The file {file_path} is not a .wav file.")
        
        self.file_path = file_path
        self.audio_file = taglib.File(self.file_path) #add error handling here as well?
        self.tags = self.audio_file.tags
        self.add_tag("ORIGINATOR", "Tech Audio")


    def add_tag(self, tag, value):
        """Adds a tag to the audio file.

        Parameters:
            tag (str): the tag key.
            value (str): the tag value.
        """
        self.tags[tag] = [str(value)]


    def remove_tag(self, tag):
        """Removes a tag from the audio file.

        Parameters:
            tag (str): the tag key.
        
        Raises:
            KeyError: If the tag does not exist in the audio file.
        """
        if tag in self.tags:
            del self.tags[tag]
        else:
            if self.logger:
                self.logger.log_error(f"Error removing tag: {tag}")
            raise KeyError(f"Tag {tag} does not exist.")


    def remove_all_tags(self):
        """Removes all tags from the audio file."""
        self.tags = {}

    def inherit_tags(self, original_file_path):
        """Inherit tags from the original audio file.

        Parameters:
            original_file_path (str): the path to the original audio file.
        """
        original_file = taglib.File(original_file_path)
        original_tags = original_file.tags
        if "INHERITED" in self.tags:
            inherited_tags = json.loads(self.tags["INHERITED"][0])
        else:
            inherited_tags = []
        inherited_tags.append({original_file_path: original_tags})
        self.tags["INHERITED"] = [json.dumps(inherited_tags)]
        if self.logger:
                self.logger.log_debug(f"Found inherited tags: {inherited_tags}.")


    def get_inherited_tags(self):
        """Gets the inherited tags from the audio file.

        Returns:
            dict: A dictionary of inherited tags, or None if there are no inherited tags.
        """
        if "INHERITED" in self.tags:
            return json.loads(self.tags["INHERITED"][0])
        else:
            return None


    def write_tags(self):
        """Writes the tags to the audio file."""
        try:
            for tag, value in self.tags.items():
                self.audio_file.tags[tag] = value
            self.audio_file.save()
            if self.logger:
                self.logger.log_debug(f"Tags written to {self.file_path}")
        except Exception as e:
            if self.logger:
                self.logger.log_error(f"Error writing tags: {e}")
            raise


    def get_tags(self):
        """Gets the current tags from the audio file.

        Returns:
            dict: A dictionary of the audio file's tags.
        """
        return self.audio_file.tags
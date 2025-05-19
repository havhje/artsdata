from birdnetlib.analyzer import Analyzer
from birdnetlib.batch import DirectoryMultiProcessingAnalyzer # Using the import from the example code after upgrade
# from birdnetlib import DirectoryMultiProcessingAnalyzer # Previous attempt
# from birdnetlib.analyzer import DirectoryMultiProcessingAnalyzer # Previous attempt for v0.0.8
from datetime import datetime
from pathlib import Path  # Added to help extract filename
import logging


def on_analyze_directory_complete(recordings, base_input_path):
    all_detections = []  # Initialize an empty list to store all detections

    for recording in recordings:
        if recording.error:
            print("Error processing this recording:", recording.error_message)
        else:
            # Augment and collect detections
            for detection in recording.detections:
                # Create a new dictionary to avoid modifying the original
                augmented_detection = detection.copy()
                # Add the filename from the recording path
                augmented_detection["filepath"] = str(recording.path)
                augmented_detection["filename"] = Path(recording.path).name
                all_detections.append(augmented_detection)

    return all_detections


# ----------------------------------------
# Hovedfunksjon for å kjøre BirdNET-analyse
# ----------------------------------------


def run_birdnet_analysis(directory_to_analyze, callback_func_from_main):
    # callback_func_from_main is functools.partial(on_analyze_directory_complete,
    # base_input_path=...)
    # on_analyze_directory_complete processes recordings and returns a list of detections.

    detections_container = []  # This list will store the final detections.

    def analysis_complete_wrapper(recordings_from_birdnet):
        # This wrapper is called by birdnetlib when analysis of all files is complete.
        # It receives the list of Recording objects.
        # callback_func_from_main is on_analyze_directory_complete(recordings,
        # base_input_path=...)
        # It processes these recordings and returns a list of detection dicts.
        count = len(recordings_from_birdnet) if recordings_from_birdnet else 0
        logging.debug(f"Analysis complete wrapper called with {count} recordings.")
        processed_detections = callback_func_from_main(recordings_from_birdnet)
        if processed_detections:
            logging.debug(f"Callback processed {len(processed_detections)} detections.")
            detections_container.extend(processed_detections)
        elif processed_detections is None:
            logging.info("User callback returned None.")
        else:  # Empty list
            logging.info("User callback returned an empty list of detections.")

    analyzer = Analyzer()
    batch = DirectoryMultiProcessingAnalyzer(
        directory_to_analyze,
        analyzers=[analyzer],
        lon=15.4244,
        lat=68.5968,
        date=datetime(year=2025, month=5, day=20),
        min_conf=0.5,
    )

    batch.on_analyze_directory_complete = analysis_complete_wrapper  # Assign wrapper
    logging.info("Starting batch processing of audio files...")
    batch.process()  # Triggers analysis_complete_wrapper
    logging.info("Batch processing finished.")

    # Problematic logging and loop accessing batch.recordings are removed.
    # Detections are in detections_container via the wrapper.

    # Section calling callback_func_from_main again is also removed.

    log_msg = (
        f"Returning {len(detections_container)} detections "
        f"from run_birdnet_analysis."
    )
    logging.info(log_msg)
    return detections_container  # Return the populated list

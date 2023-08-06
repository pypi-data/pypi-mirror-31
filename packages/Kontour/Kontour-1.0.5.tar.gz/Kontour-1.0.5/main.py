from Score import Score
from Analyse import Analyse
from music21 import stream, environment
import argparse
import os.path


def Main():

    if not(os.path.isdir('Results')):
        os.mkdir('Results')
    if not(os.path.isdir('Music')):
        os.mkdir('Music')

    # Create parser object
    parser = argparse.ArgumentParser(prog="main", description="Finds common melodic phrases in **kern encoded music.")

    # Define argument groups
    filename_group = parser.add_mutually_exclusive_group(required=True)
    viewer_group = parser.add_argument_group("Export Options", "Allows the user to specify how to view the results.")
    search_group = parser.add_argument_group("Search Options", "Different search options.")

    # Add argument options to each group
    filename_group.add_argument("-f", "--filename", help="Takes one argument; the name of the file")
    search_group.add_argument("-s", "--sequence", help="User can enter a sequnce to search for using the alphabet {+,-,0}.")
    viewer_group.add_argument("-ms", "--musescore", help="Indicates if the user want to view the results in MuseScore.", action="store_true")
    viewer_group.add_argument("-pdf", "--lillypond", help="Indicates that the user wants to export the results to pdf using LillyPond.", action="store_true")

    # Collect the CLI arguments
    args = parser.parse_args()

    # Get the name of the score (REQUIRED)
    score = Score(args.filename)

    # If user want to export to MuseScore and pdf
    if (args.musescore and args.lillypond):
        # Export the composition to PDF with Lilypond
        score.parsed_score.write('lily.pdf', fp = 'Results/' + score.name)
        # Load the composition in MuseScore2
        score.parsed_score.show()
        # Tell pattern engine to export to MusicXML and PDF
        pattern_engine = Analyse(["MuseScore","LillyPond"], score)
        # If user specified a sequnce
        if args.sequence:
            pattern_engine.Search_Score(score.name, args.sequence)

        # If no sequnce is specified
        elif not(args.sequence):
            # Run the pattern engine to find common patterns in the composition
            patterns = pattern_engine.common_patterns(score.contour_abstract)
            # Find every found pattern in the score
            for match in patterns:
                score = Score(args.filename)
                pattern_engine.score_refresh(score)
                pattern_engine.Search_Score(score.name, match)

    elif (args.musescore) or (not(args.musescore) and not(args.lillypond)):
        # Load the composition in MuseScore2
        score.parsed_score.show()
        # Tell pattern engine to export to MusicXML
        pattern_engine = Analyse(["MuseScore"], score)

        # If user specified a sequnce
        if args.sequence:
            pattern_engine.Search_Score(score.name, args.sequence)

        # If no sequnce is specified
        elif not(args.sequence):
            # Run the pattern engine to find common patterns in the composition
            patterns = pattern_engine.common_patterns(score.contour_abstract)
            # Find every found pattern in the score
            for match in patterns:
                score = Score(args.filename)
                pattern_engine.score_refresh(score)
                pattern_engine.Search_Score(score.name, match)


    elif args.lillypond:
        # Export the composition to PDF with Lilypond
        score.parsed_score.write('lily.pdf', fp = 'Results/' + score.name)
        pattern_engine = Analyse(["LillyPond"], score)

        #If user specified a sequnce
        if args.sequence:
            # Search for the sequnce in the composition
            pattern_engine.Search_Score(score.name, args.sequence)

        # If no sequnce is specified
        elif not(args.sequence):
            # Run the pattern engine to find common patterns in the composition
            patterns = pattern_engine.common_patterns(score.contour_abstract)
            # Find every found pattern in the score
            for match in patterns:
                score = Score(args.filename)
                pattern_engine.score_refresh(score)
                pattern_engine.Search_Score(score.name, match)


if __name__ == "__main__":
    Main()

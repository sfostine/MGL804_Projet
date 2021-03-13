import org.apache.commons.cli.*;

import java.io.File;

/**
 * //https://stackoverflow.com/questions/7341683/parsing-arguments-to-a-java-command-line-program
 */
public class ArgumentHandler {

    private final String inputFolderPath;
    private final String outputFolderPath;
    private final String commit;

    public ArgumentHandler(String[] args) {
        //      todo: debug args bellow
//        String[] testArgs =
//                {"-i", "C:/workspace/MGL804_Projet/src/main/java", "-o", "asdfadsffaf"};
//        args = testArgs.clone();
//        System.out.println(args[0]);

        CommandLine commandLine = null;
        CommandLineParser parser = new DefaultParser();
        HelpFormatter formatter = new HelpFormatter();
        Options options = new Options();

        Option option_i = Option.builder("i")
                .required(true)
                .desc("Input source folder path")
                .longOpt("Input")
                .argName("Input")
                .build();
        Option option_o = Option.builder("o")
                .required(true)
                .desc("Path to the output folder")
                .longOpt("Output")
                .argName("Output")
                .build();
        Option option_c = Option.builder("b")
                .required(true)
                .desc("The branch name in GitHub.")
                .longOpt("Branch")
                .argName("Branch")
                .build();

        options.addOption(option_i);
        options.addOption(option_o);
        options.addOption(option_c);

        try {
            commandLine = parser.parse(options, args);
        } catch (ParseException exception) {
            System.out.println(exception.getMessage());
            formatter.printHelp("Refactorite", options);
            System.out.println("Quitting..");
            System.exit(1);
        }

        if (commandLine == null) {
            System.out.println("Couldn't parse the command line arguments.");
            formatter.printHelp("Refactorite", options);
            System.out.println("Quitting..");
            System.exit(2);
        }

        this.inputFolderPath = commandLine.getArgs()[0];
        this.outputFolderPath = commandLine.getArgs()[1];
        this.commit = commandLine.getArgs()[2];

        try {
            validateArgs(inputFolderPath, outputFolderPath);
        } catch (IllegalArgumentException exception) {
            System.out.println(exception.getMessage());
            System.out.println("Quitting..");
            System.exit(3);
        }

    }

    private void validateArgs(String input, String output) {
        if (input == null) {
            throw new IllegalArgumentException("Input source folder is not specified.");
        } else {
            File folder = new File(input);
            if (folder.exists() && folder.isDirectory()) {
                File outFolder = new File(output);
                if (outFolder.exists() && outFolder.isFile()) {
                    throw new IllegalArgumentException("The specified output folder path is not valid.");
                }
            } else {
                throw new IllegalArgumentException("Input source folder path is not valid.");
            }
        }
    }

    public String getOutputFolderPath() {
        return outputFolderPath;
    }

    public String getInputFolderPath() {
        return inputFolderPath;
    }

    public String getCommit() {
        return commit;
    }
}

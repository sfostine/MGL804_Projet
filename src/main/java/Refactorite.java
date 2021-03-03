//    todo: https://www.baeldung.com/executable-jar-with-maven

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.List;

import org.apache.commons.cli.*;
import org.eclipse.jgit.lib.Repository;
import org.json.JSONObject;
import org.refactoringminer.api.GitHistoryRefactoringMiner;
import org.refactoringminer.api.GitService;
import org.refactoringminer.api.Refactoring;
import org.refactoringminer.api.RefactoringHandler;
import org.refactoringminer.rm1.GitHistoryRefactoringMinerImpl;
import org.refactoringminer.util.GitServiceImpl;

public class Refactorite {

    //https://stackoverflow.com/questions/7341683/parsing-arguments-to-a-java-command-line-program
    public static void main(String[] args) throws Exception {
//      todo: debug args bellow
        String[] testArgs =
                {"-i", "C:/workspace/MGL804_Projet/src/main/java", "-o", "asdfadsffaf"};
        args = testArgs.clone();
        System.out.println(args[0]);

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

        options.addOption(option_i);
        options.addOption(option_o);

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

        String inputFolderPath = commandLine.getOptionValue(option_i.getOpt());
        String outputFolderPath = commandLine.getOptionValue(option_o.getOpt());

        try {
            validateArgs(inputFolderPath, outputFolderPath);
        } catch (IllegalArgumentException exception) {
            System.out.println(exception.getMessage());
            System.out.println("Quitting..");
            System.exit(3);
        }


        DetectRefactoringInSystem("tmp/xerces", "https://github.com/apache/xerces2-j.git", "trunk", "tmp/JsonOutput/xerces.json");
    }

    private static void validateArgs(String input, String output) {
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

    private static void DetectRefactoringInSystem(String cloningFolder, String gitPath, String branch, String outputFileName) throws Exception {
        GitService gitService = new GitServiceImpl();
        GitHistoryRefactoringMiner miner = new GitHistoryRefactoringMinerImpl();

        System.out.println("Cloning from " + gitPath);
        Repository repo = gitService.cloneIfNotExists(cloningFolder, gitPath);
        System.out.println("Done cloning!");

        JSONObject jsonObject = new JSONObject();

        RefactoringHandler handler = new RefactoringHandler() {
            @Override
            public void handle(String commitId, List<Refactoring> refactorings) {
                System.out.println("Refactorings at " + commitId);

                for (Refactoring ref : refactorings) {
                    System.out.println("Appending value " + ref.toJSON());
                    jsonObject.append(commitId, ref.toJSON());
                }
            }

            @Override
            public void handleException(String commitId, Exception e) {
                System.out.println("Exception at commit " + commitId + " : " + e.getMessage());
            }
        };

        System.out.println("detect refactorings from commits");
        miner.detectAll(repo, branch, handler);
        System.out.println("Done!!!");

        System.out.println("Creating file " + outputFileName);
        WriteToFile(outputFileName, jsonObject);
        System.out.println("File " + outputFileName + " is created!");

    }

    private static void WriteToFile(String outputFileName, JSONObject jsonObject) throws IOException {
        FileWriter file = new FileWriter(outputFileName);
        try {
            file.write(jsonObject.toString(3));
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            file.close();
        }
    }
}

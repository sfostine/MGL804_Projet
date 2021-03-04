import org.eclipse.jgit.lib.Repository;
import org.refactoringminer.api.GitHistoryRefactoringMiner;
import org.refactoringminer.api.GitService;
import org.refactoringminer.api.Refactoring;
import org.refactoringminer.api.RefactoringHandler;
import org.refactoringminer.rm1.GitHistoryRefactoringMinerImpl;
import org.refactoringminer.util.GitServiceImpl;

import java.io.FileWriter;
import java.io.IOException;
import java.util.List;

/**
 * https://github.com/tsantalis/RefactoringMiner
 */
public class Refactorite {
    public static void main(String[] args) throws Exception {
        // LOAD CONFIGURATION todo: remove cfg if not needed
        // JSONObject cfg = new Configuration();

        // ARGUMENTS OPTION HANDLING
        ArgumentHandler arg = new ArgumentHandler(args);
        String inputFolderPath = arg.getInputFolderPath();
        String outputFolderPath = arg.getOutputFolderPath();
        String commit = arg.getCommit();

        // RUN PROGRAM
        detectRefactoringAtCommit(commit, inputFolderPath, outputFolderPath);
        //  DetectRefactoringInSystem("tmp/xerces", "https://github.com/apache/xerces2-j.git", "trunk", "tmp/JsonOutput/xerces.json");
    }

    private static void detectRefactoringAtCommit(String commit, String inputFolderPath, String outputFolderPath) {
        GitService gitService = new GitServiceImpl();
        GitHistoryRefactoringMiner miner = new GitHistoryRefactoringMinerImpl();

        try {
            Repository repo = gitService.openRepository(inputFolderPath);
            miner.detectAtCommit(repo, commit, new RefactoringHandler() {
                @Override
                public void handle(String commitId, List<Refactoring> refactorings) {
                    System.out.println("Refactorings at " + commitId);
                    for (Refactoring ref : refactorings) {
                        // System.out.println(ref.toJSON());
                        //Write JSON file
                        try (FileWriter file = new FileWriter(outputFolderPath + "\\report_" + commit + ".json")) {
                            //We can write any JSONArray or JSONObject instance to the file
                            file.write(ref.toJSON());
                            file.flush();
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                    }
                }
            });

        } catch (Exception e) {
            e.printStackTrace();
        }
    }


//    private static void DetectRefactoringInSystem(String cloningFolder, String gitPath, String branch, String outputFileName) throws Exception {
//        GitService gitService = new GitServiceImpl();
//        GitHistoryRefactoringMiner miner = new GitHistoryRefactoringMinerImpl();
//
//        System.out.println("Cloning from " + gitPath);
//        Repository repo = gitService.cloneIfNotExists(cloningFolder, gitPath);
//        System.out.println("Done cloning!");
//
//        JSONObject jsonObject = new JSONObject();
//
//        RefactoringHandler handler = new RefactoringHandler() {
//            @Override
//            public void handle(String commitId, List<Refactoring> refactorings) {
//                System.out.println("Refactorings at " + commitId);
//
//                for (Refactoring ref : refactorings) {
//                    System.out.println("Appending value " + ref.toJSON());
//                    jsonObject.put(commitId, ref.toJSON());
//                }
//            }
//
//            @Override
//            public void handleException(String commitId, Exception e) {
//                System.out.println("Exception at commit " + commitId + " : " + e.getMessage());
//            }
//        };
//
//        System.out.println("detect refactorings from commits");
//        miner.detectAll(repo, branch, handler);
//        System.out.println("Done!!!");
//
//        System.out.println("Creating file " + outputFileName);
//        WriteToFile(outputFileName, jsonObject);
//        System.out.println("File " + outputFileName + " is created!");
//
//    }
//
//    private static void WriteToFile(String outputFileName, JSONObject jsonObject) throws IOException {
//        FileWriter file = new FileWriter(outputFileName);
//        try {
//            file.write(jsonObject.toJSONString());
//        } catch (IOException e) {
//            e.printStackTrace();
//        } finally {
//            file.close();
//        }
//    }
}

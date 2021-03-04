import java.io.FileWriter;
import java.io.IOException;
import java.util.List;

import org.eclipse.jgit.lib.Repository;
import org.json.simple.JSONObject;
import org.refactoringminer.api.GitHistoryRefactoringMiner;
import org.refactoringminer.api.GitService;
import org.refactoringminer.api.Refactoring;
import org.refactoringminer.api.RefactoringHandler;
import org.refactoringminer.rm1.GitHistoryRefactoringMinerImpl;
import org.refactoringminer.util.GitServiceImpl;

public class Refactorite {
    public static void main(String[] args) throws Exception {
        // LOAD CONFIGURATION
        JSONObject cfg = new Configuration();
        System.out.println(cfg.get("paths"));

        // ARGUMENTS OPTION HANDLING
        ArgumentHandler arg = new ArgumentHandler(args);
        String inputFolderPath = arg.getInputFolderPath();
        String outputFolderPath = arg.getOutputFolderPath();

        // RUN PROGRAM
        DetectRefactoringInSystem("tmp/xerces", "https://github.com/apache/xerces2-j.git", "trunk", "tmp/JsonOutput/xerces.json");
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
                    jsonObject.put(commitId, ref.toJSON());
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
            file.write(jsonObject.toJSONString());
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            file.close();
        }
    }
}

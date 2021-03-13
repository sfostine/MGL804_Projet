import com.fasterxml.jackson.databind.ObjectMapper;
import org.eclipse.jgit.lib.Repository;
import org.refactoringminer.api.GitHistoryRefactoringMiner;
import org.refactoringminer.api.GitService;
import org.refactoringminer.api.Refactoring;
import org.refactoringminer.api.RefactoringHandler;
import org.refactoringminer.rm1.GitHistoryRefactoringMinerImpl;
import org.refactoringminer.util.GitServiceImpl;

import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * https://github.com/tsantalis/RefactoringMiner
 */
public class Refactorite {
    public static void main(String[] args) throws Exception {
        // ARGUMENTS OPTION HANDLING
        ArgumentHandler arg = new ArgumentHandler(args);
        String inputFolderPath = arg.getInputFolderPath();
        String outputFolderPath = arg.getOutputFolderPath();
        String branch = arg.getCommit();

        System.out.println("Detect Refactoring..."
                + "\n\tbranch: " + branch
                + "\n\tinputFolderPath: " + inputFolderPath
                + "\n\toutputFolderPath: " + outputFolderPath
        );
        // RUN PROGRAM
        detectRefactoring(branch, inputFolderPath, outputFolderPath);
    }

    private static void detectRefactoring(String branch, String inputFolderPath, String outputFolderPath) {
        GitService gitService = new GitServiceImpl();
        GitHistoryRefactoringMiner miner = new GitHistoryRefactoringMinerImpl();

        try {
            Repository repo = gitService.openRepository(inputFolderPath);
            miner.detectAll(repo, branch, new RefactoringHandler() {
                private String prevCommitId = "";

                @Override
                public void handle(String commitId, List<Refactoring> refactorings) {
                    System.out.println("\tcommitId: " + commitId);
                    ArrayList refLst = new ArrayList<Map>();
                    for (Refactoring ref : refactorings) {
                        ObjectMapper mapper = new ObjectMapper();
                        try {
                            Map<String, String> map = mapper.readValue(ref.toJSON(), Map.class);
                            refLst.add(map);
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                    }
                    if (refLst.size() > 0) {
                        Map<String, Object> jsonMap = new HashMap<>();
                        jsonMap.put("commitId", commitId);
                        jsonMap.put("prevCommitId", prevCommitId);
                        jsonMap.put("refactorings", refLst);
                        save_json(jsonMap, outputFolderPath);
                    }
                    prevCommitId = commitId;
                }

                private void save_json(Map<String, Object> data, String outputFolderPath) {
                    try {
                        FileWriter file = new FileWriter(outputFolderPath + '\\' + data.get("commitId") + ".json");
                        ObjectMapper mapper = new ObjectMapper();
                        String json = mapper.writerWithDefaultPrettyPrinter().writeValueAsString(data);

                        file.write(json);
                        file.flush();
                    } catch (IOException e) {
                        e.printStackTrace();
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

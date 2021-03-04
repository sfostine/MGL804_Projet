//import org.json.simple.JSONArray;
//import org.json.simple.JSONObject;
//import org.json.simple.parser.JSONParser;
//
//import java.nio.file.Files;
//import java.nio.file.Paths;
//import java.io.IOException;
//
//import org.json.simple.parser.ParseException;
//
//
//public class Configuration extends JSONObject {
//
//    public Configuration() {
//        super(get_config());
//    }
//
//    private static JSONObject get_config() {
//        JSONObject json = null;
//        try {
//            String jsonStr = new String(Files.readAllBytes(Paths.get("src\\main\\resources\\config.json")));
//            jsonStr = "[" + jsonStr + "]";
//            JSONParser parser = new JSONParser();
//            Object obj = parser.parse(jsonStr);
//
//            JSONArray array = (JSONArray) obj;
//            json = (JSONObject) array.get(0);
//
//        } catch (IOException | ParseException e) {
//            e.printStackTrace();
//        }
//
//        return json;
//
//    }
//
//
//}

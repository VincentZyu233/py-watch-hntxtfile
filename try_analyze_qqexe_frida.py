import frida
import sys

session = frida.attach("QQ.exe")

script = session.create_script("""
Interceptor.attach(Module.getExportByName(null, "SendMessageW"), {
    onEnter: function (args) {
        var hwnd = args[0];
        var msg = args[1];
        var wparam = args[2];
        var lparam = args[3];
        
        // 捕获输入文本等
        if (msg == 0x000C) { // WM_SETTEXT
            console.log("[WM_SETTEXT] hwnd: " + hwnd + ", text: " + Memory.readUtf16String(lparam));
        }

        if (msg == 0x0100 && wparam == 13) {
            console.log("[ENTER] Enter 键被按下");
        }
    }
});
""")

script.on("message", lambda msg, data: print("[*] {}".format(msg)))
script.load()

sys.stdin.read()

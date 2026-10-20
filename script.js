async function sendAiQuestion(){
    const userQuestion = document.getElementById("aiInput").value.trim();
    if(!userQuestion){
        alert("请输入你的问题！");
        return;
    }
    const resultBox = document.getElementById("aiResult");

    // 本地知识库优先检索
    const localAnswer = searchKnowledge(userQuestion);
    if(localAnswer !== null){
        resultBox.innerText = `【本地知识库】\n${localAnswer}`;
        return;
    }

    resultBox.innerText = "AI正在思考中……";
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 12000);

        const res = await fetch("http://127.0.0.1:5002/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: userQuestion }),
            signal: controller.signal
        });
        clearTimeout(timeoutId);

        // 流式解析
        resultBox.innerText = "";
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            buffer = lines.pop();

            for (const line of lines) {
                if (line.startsWith("data: ")) {
                    const dataStr = line.slice(6);
                    if (dataStr === "[DONE]") continue;
                    try {
                        const json = JSON.parse(dataStr);
                        if (json.content) {
                            resultBox.innerText += json.content;
                        }
                    } catch (e) {}
                }
            }
        }
    } catch (err) {
        if(err.name === "AbortError"){
            resultBox.innerText = "请求超时，请检查后端服务";
        } else {
            resultBox.innerText = "请求失败：" + err;
            console.error(err);
        }
    }
}
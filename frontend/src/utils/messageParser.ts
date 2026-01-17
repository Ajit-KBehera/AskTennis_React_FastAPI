export interface DisplayMessageInfo {
    label: string;
    labelClass: string;
    content: string;
    isCodeBlock?: boolean;
}

export const parseMessageForDisplay = (msg: any): DisplayMessageInfo => {
    const type = msg.type;
    const content = msg.content;

    if (type === 'HumanMessage') {
        const displayContent = typeof content === 'string' ? content : JSON.stringify(content);
        return {
            label: '👤 Human:',
            labelClass: 'text-blue-300',
            content: displayContent
        };
    }

    if (type === 'AIMessage') {
        let textContent = "";
        if (Array.isArray(content)) {
            for (const part of content) {
                if (typeof part === 'string') {
                    textContent += part;
                } else if (typeof part === 'object' && part !== null) {
                    textContent += part.text || JSON.stringify(part);
                }
            }
        } else {
            textContent = String(content);
        }

        if (!textContent && msg.tool_calls && msg.tool_calls.length > 0) {
            const toolNames = msg.tool_calls.map((tc: any) => tc.name).join(', ');
            textContent = `🔧 Calling tool(s): ${toolNames}`;
        } else if (!textContent) {
            textContent = "*[No text content]*";
        }

        return {
            label: '🤖 AI:',
            labelClass: 'text-emerald-300',
            content: textContent
        };
    }

    if (type === 'ToolMessage') {
        let contentStr = String(content);
        if (contentStr.length > 500) {
            contentStr = contentStr.substring(0, 500) + "...";
        }
        return {
            label: '🔧 Tool Response:',
            labelClass: 'text-amber-300',
            content: contentStr,
            isCodeBlock: true
        };
    }

    // Fallback
    let displayContent = String(content);
    if (displayContent.length > 200) {
        displayContent = displayContent.substring(0, 200) + "...";
    }
    return {
        label: `📝 ${type}:`,
        labelClass: 'text-gray-400',
        content: displayContent
    };
};

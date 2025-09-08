/**
 * GenHuman API 成功工作流程 - 基於前端驗證的完整實現
 * 
 * 📋 完整流程：免費聲音克隆 → 付費聲音合成 → 免費數字人克隆 → 付費數字人合成
 * 
 * ✅ 前端測試驗證：所有步驟均已在前端成功測試
 * 🎯 適用場景：後端快速复制前端成功經驗
 */

class GenHumanAPIWorkflow {
    constructor(apiToken) {
        this.apiBase = 'https://api.yidevs.com';
        this.token = apiToken || '08D7EE7F91D258F27B4ADDF59CDDDEDE.1E95F76130BA23D37CE7BBBD69B19CCF.KYBVDWNR';
        this.workflowData = {
            voiceId: null,
            audioUrl: null,
            digitalHumanId: null,
            taskId: null
        };
    }

    /**
     * 通用API調用方法
     */
    async callAPI(endpoint, data, method = 'POST') {
        const url = this.apiBase + endpoint;
        
        console.log(`🚀 [${new Date().toLocaleTimeString()}] 調用API: ${method} ${endpoint}`);
        console.log(`📊 請求數據:`, data);
        
        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    token: this.token,
                    ...data
                })
            });
            
            const result = await response.json();
            console.log(`📥 API響應 (${response.status}):`, result);
            
            return {
                success: response.ok && result.code === 200,
                data: result,
                status: response.status
            };
        } catch (error) {
            console.error(`❌ API調用失敗:`, error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 步驟1：免費聲音克隆
     * 
     * @param {string} voiceName - 聲音名稱
     * @param {string} voiceUrl - 音頻文件URL
     * @param {string} describe - 聲音描述
     * @returns {Promise<{success: boolean, voiceId?: string}>}
     */
    async step1_VoiceClone(voiceName, voiceUrl, describe = '清晰標準聲音') {
        console.log(`🎤 ===== 步驟1：免費聲音克隆 =====`);
        console.log(`📋 聲音名稱: ${voiceName}`);
        console.log(`🔗 音頻URL: ${voiceUrl}`);
        
        const response = await this.callAPI('/app/human/human/Voice/clone', {
            voice_name: voiceName,
            voice_url: voiceUrl,
            describe: describe
        });
        
        if (response.success && response.data.code === 200) {
            this.workflowData.voiceId = response.data.data.voice_id;
            console.log(`✅ 聲音克隆成功！Voice ID: ${this.workflowData.voiceId}`);
            
            return {
                success: true,
                voiceId: this.workflowData.voiceId,
                data: response.data
            };
        } else {
            console.error(`❌ 聲音克隆失敗:`, response.data || response.error);
            return {
                success: false,
                error: response.data || response.error
            };
        }
    }

    /**
     * 步驟2：付費聲音合成
     * 
     * @param {string} text - 要合成的文字
     * @param {string} voiceId - 步驟1獲得的voice_id（可選，默認使用工作流中的）
     * @returns {Promise<{success: boolean, audioUrl?: string}>}
     */
    async step2_VoiceSynthesis(text, voiceId = null) {
        console.log(`🔊 ===== 步驟2：付費聲音合成 =====`);
        
        const targetVoiceId = voiceId || this.workflowData.voiceId;
        if (!targetVoiceId) {
            console.error(`❌ 缺少voice_id，請先執行步驟1`);
            return { success: false, error: '缺少voice_id，請先執行步驟1' };
        }
        
        console.log(`📋 使用Voice ID: ${targetVoiceId}`);
        console.log(`📝 合成文字: ${text}`);
        
        const response = await this.callAPI('/app/human/human/Voice/synthesis', {
            voice_id: targetVoiceId,
            text: text
        });
        
        if (response.success && response.data.code === 200) {
            this.workflowData.audioUrl = response.data.data.audio_url;
            console.log(`✅ 聲音合成成功！Audio URL: ${this.workflowData.audioUrl}`);
            
            return {
                success: true,
                audioUrl: this.workflowData.audioUrl,
                data: response.data
            };
        } else {
            console.error(`❌ 聲音合成失敗:`, response.data || response.error);
            return {
                success: false,
                error: response.data || response.error
            };
        }
    }

    /**
     * 步驟3：免費數字人克隆
     * 
     * @param {string} characterName - 角色名稱
     * @param {string} imageUrl - 人物照片URL
     * @returns {Promise<{success: boolean, digitalHumanId?: string}>}
     */
    async step3_DigitalHumanClone(characterName, imageUrl) {
        console.log(`👤 ===== 步驟3：免費數字人克隆 =====`);
        console.log(`📋 角色名稱: ${characterName}`);
        console.log(`🖼️ 照片URL: ${imageUrl}`);
        
        const response = await this.callAPI('/app/human/human/Index/humanClone', {
            character_name: characterName,
            image_url: imageUrl
        });
        
        if (response.success && response.data.code === 200) {
            this.workflowData.digitalHumanId = response.data.data.digital_human_id;
            console.log(`✅ 數字人克隆成功！Digital Human ID: ${this.workflowData.digitalHumanId}`);
            
            return {
                success: true,
                digitalHumanId: this.workflowData.digitalHumanId,
                data: response.data
            };
        } else {
            console.error(`❌ 數字人克隆失敗:`, response.data || response.error);
            return {
                success: false,
                error: response.data || response.error
            };
        }
    }

    /**
     * 步驟4：付費數字人合成（最終步驟）
     * 
     * @param {string} callbackUrl - 回調地址
     * @param {string} audioUrl - 步驟2獲得的音頻URL（可選，默認使用工作流中的）
     * @param {string} digitalHumanId - 步驟3獲得的數字人ID（可選，默認使用工作流中的）
     * @returns {Promise<{success: boolean, taskId?: string}>}
     */
    async step4_DigitalHumanSynthesis(callbackUrl, audioUrl = null, digitalHumanId = null) {
        console.log(`🎬 ===== 步驟4：付費數字人合成 =====`);
        
        const targetAudioUrl = audioUrl || this.workflowData.audioUrl;
        const targetDigitalHumanId = digitalHumanId || this.workflowData.digitalHumanId;
        
        if (!targetAudioUrl || !targetDigitalHumanId) {
            console.error(`❌ 缺少必要參數，請先執行步驟2和步驟3`);
            return { 
                success: false, 
                error: '缺少必要參數：audioUrl或digitalHumanId' 
            };
        }
        
        console.log(`📋 回調URL: ${callbackUrl}`);
        console.log(`🔊 音頻URL: ${targetAudioUrl}`);
        console.log(`👤 數字人ID: ${targetDigitalHumanId}`);
        
        const response = await this.callAPI('/app/human/human/Index/created', {
            callback_url: callbackUrl,
            scene_task_id: targetDigitalHumanId,
            audio_address: targetAudioUrl
        });
        
        if (response.success && response.data.code === 200) {
            this.workflowData.taskId = response.data.data.video_task_id;
            console.log(`✅ 數字人合成任務提交成功！Task ID: ${this.workflowData.taskId}`);
            
            return {
                success: true,
                taskId: this.workflowData.taskId,
                data: response.data
            };
        } else {
            console.error(`❌ 數字人合成失敗:`, response.data || response.error);
            return {
                success: false,
                error: response.data || response.error
            };
        }
    }

    /**
     * 查詢任務狀態
     * 
     * @param {string} taskId - 任務ID（可選，默認使用工作流中的）
     * @returns {Promise<{success: boolean, status?: number, videoUrl?: string}>}
     */
    async queryTaskStatus(taskId = null) {
        const targetTaskId = taskId || this.workflowData.taskId;
        if (!targetTaskId) {
            console.error(`❌ 缺少task_id，請先執行步驟4`);
            return { success: false, error: '缺少task_id，請先執行步驟4' };
        }
        
        console.log(`🔍 查詢任務狀態: ${targetTaskId}`);
        
        const response = await this.callAPI('/app/human/human/Musetalk/task', {
            task_id: targetTaskId
        }, 'GET');
        
        if (response.success && response.data.code === 200) {
            const taskData = response.data.data;
            const status = taskData.state;
            
            let statusText = '';
            switch(status) {
                case 10: statusText = '處理中'; break;
                case 20: statusText = '已完成'; break;
                case 30: statusText = '失敗'; break;
                default: statusText = '未知狀態';
            }
            
            console.log(`📊 任務狀態: ${statusText} (${status})`);
            
            if (status === 20 && taskData.videoUrl) {
                console.log(`🎉 任務完成！視頻URL: ${taskData.videoUrl}`);
                return {
                    success: true,
                    status: status,
                    videoUrl: taskData.videoUrl,
                    data: response.data
                };
            } else if (status === 30) {
                console.log(`❌ 任務失敗`);
                return {
                    success: false,
                    status: status,
                    error: '任務處理失敗',
                    data: response.data
                };
            } else {
                console.log(`⏳ 任務仍在處理中`);
                return {
                    success: true,
                    status: status,
                    processing: true,
                    data: response.data
                };
            }
        } else {
            console.error(`❌ 查詢失敗:`, response.data || response.error);
            return {
                success: false,
                error: response.data || response.error
            };
        }
    }

    /**
     * 完整工作流程自動執行
     * 
     * @param {Object} params - 參數對象
     * @param {string} params.voiceName - 聲音名稱
     * @param {string} params.voiceUrl - 音頻文件URL
     * @param {string} params.text - 要合成的文字
     * @param {string} params.characterName - 角色名稱
     * @param {string} params.imageUrl - 人物照片URL
     * @param {string} params.callbackUrl - 回調地址
     * @returns {Promise<{success: boolean, results: Object}>}
     */
    async executeFullWorkflow(params) {
        console.log(`🚀 ===== 開始執行完整GenHuman工作流程 =====`);
        console.log(`📋 參數:`, params);
        
        const results = {
            step1: null,
            step2: null,
            step3: null,
            step4: null,
            final: null
        };
        
        try {
            // 步驟1：聲音克隆
            results.step1 = await this.step1_VoiceClone(params.voiceName, params.voiceUrl);
            if (!results.step1.success) {
                throw new Error(`步驟1失敗: ${results.step1.error}`);
            }
            
            // 步驟2：聲音合成
            results.step2 = await this.step2_VoiceSynthesis(params.text);
            if (!results.step2.success) {
                throw new Error(`步驟2失敗: ${results.step2.error}`);
            }
            
            // 步驟3：數字人克隆
            results.step3 = await this.step3_DigitalHumanClone(params.characterName, params.imageUrl);
            if (!results.step3.success) {
                throw new Error(`步驟3失敗: ${results.step3.error}`);
            }
            
            // 步驟4：數字人合成
            results.step4 = await this.step4_DigitalHumanSynthesis(params.callbackUrl);
            if (!results.step4.success) {
                throw new Error(`步驟4失敗: ${results.step4.error}`);
            }
            
            console.log(`✅ 完整工作流程執行成功！`);
            console.log(`📊 最終結果:`, {
                voiceId: this.workflowData.voiceId,
                audioUrl: this.workflowData.audioUrl,
                digitalHumanId: this.workflowData.digitalHumanId,
                taskId: this.workflowData.taskId
            });
            
            return {
                success: true,
                results: results,
                workflowData: this.workflowData
            };
            
        } catch (error) {
            console.error(`❌ 工作流程執行失敗:`, error.message);
            return {
                success: false,
                error: error.message,
                results: results
            };
        }
    }

    /**
     * 獲取當前工作流程數據
     */
    getWorkflowData() {
        return this.workflowData;
    }

    /**
     * 重置工作流程數據
     */
    resetWorkflow() {
        this.workflowData = {
            voiceId: null,
            audioUrl: null,
            digitalHumanId: null,
            taskId: null
        };
        console.log(`🔄 工作流程數據已重置`);
    }
}

// 使用範例
export async function exampleUsage() {
    // 初始化工作流程
    const workflow = new GenHumanAPIWorkflow();
    
    // 方式一：分步執行
    console.log('=== 分步執行示例 ===');
    
    const step1Result = await workflow.step1_VoiceClone(
        '測試聲音',
        'https://example.com/audio.mp3'
    );
    
    if (step1Result.success) {
        const step2Result = await workflow.step2_VoiceSynthesis(
            '大家好，我是數字人助手。'
        );
        
        if (step2Result.success) {
            // 繼續後續步驟...
        }
    }
    
    // 方式二：完整自動執行
    console.log('=== 完整自動執行示例 ===');
    
    const fullResult = await workflow.executeFullWorkflow({
        voiceName: '測試聲音',
        voiceUrl: 'https://example.com/audio.mp3',
        text: '大家好，我是數字人助手，很高興為您服務。',
        characterName: 'Andy老師',
        imageUrl: 'https://example.com/photo.jpg',
        callbackUrl: 'https://your-domain.com/callback'
    });
    
    if (fullResult.success) {
        console.log('🎉 完整工作流程執行成功！');
        
        // 查詢任務狀態
        const statusResult = await workflow.queryTaskStatus();
        console.log('任務狀態:', statusResult);
    }
}

// PHP後端對應實現提示
export const phpImplementationTips = {
    step1: {
        endpoint: '/app/human/human/Voice/clone',
        method: 'POST',
        params: ['token', 'voice_name', 'voice_url', 'describe'],
        response: 'voice_id in data.voice_id'
    },
    step2: {
        endpoint: '/app/human/human/Voice/synthesis',
        method: 'POST',
        params: ['token', 'voice_id', 'text'],
        response: 'audio_url in data.audio_url'
    },
    step3: {
        endpoint: '/app/human/human/Index/humanClone',
        method: 'POST',
        params: ['token', 'character_name', 'image_url'],
        response: 'digital_human_id in data.digital_human_id'
    },
    step4: {
        endpoint: '/app/human/human/Index/created',
        method: 'POST',
        params: ['token', 'callback_url', 'scene_task_id', 'audio_address'],
        response: 'video_task_id in data.video_task_id'
    },
    query: {
        endpoint: '/app/human/human/Musetalk/task',
        method: 'GET',
        params: ['token', 'task_id'],
        response: 'state and videoUrl in data'
    }
};

export default GenHumanAPIWorkflow;

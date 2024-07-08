export OPENAI_API_KEY="EMPTY"
# export OPENAI_API_BASE="https://api.endpoints.anyscale.com/v1"
export OPENAI_API_BASE="http://localhost:8000/v1"

# python token_benchmark_ray.py \
python openai_multi_steam_req.py \
--model "glm4" \
--mean-input-tokens 550 \
--stddev-input-tokens 150 \
--mean-output-tokens 150 \
--stddev-output-tokens 10 \
--max-num-completed-requests 20 \
--timeout 600 \
--num-concurrent-requests 1 \
--results-dir "result_outputs_qwen" \
--llm-api openai \
--additional-sampling-params '{}'

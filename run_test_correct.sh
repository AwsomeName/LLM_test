export OPENAI_API_KEY="EMPTY"
# export OPENAI_API_BASE="https://api.endpoints.anyscale.com/v1"
export OPENAI_API_BASE="http://localhost:8000/v1"

# python token_benchmark_ray.py \
python llm_correctness.py \
--max-num-completed-requests 50 \
--num-concurrent-requests 10 \
--model "glm4" \
--timeout 600 \
--results-dir "result_correct_qwen" \
--llm-api openai \

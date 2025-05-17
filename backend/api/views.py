from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from api.processor.decision_processor import DecisionProcessor
from chroma_client.chroma_storage import ChromaDBHandler
from collections import defaultdict

import logging
logger = logging.getLogger(__name__)


class DecisionUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        input_text = request.data.get("input_text")
        if not input_text:
            return Response({"error": "You need to pass a URLs."}, status=status.HTTP_400_BAD_REQUEST)

        processor = DecisionProcessor(input_text)
        processor.extract_ids()

        if not processor.decision_ids:
            return Response({"error": "No decision IDs found in input_text."}, status=status.HTTP_400_BAD_REQUEST)

        user_channel_id = self.request.user.uuid_channel

        set_tasks = processor.process_all(user_channel_id)
        message = f"Successfully sent {len(set_tasks)} decision for processing"
        result = {"message": message}

        return Response(result, status=status.HTTP_200_OK)


class SearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        search_words = request.data.get("search")

        if not search_words or not search_words.strip():
            return Response({"error": "You need to pass a few key words."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            db_handler = ChromaDBHandler()
            db_handler.init_embedding_model()

            # 1 similarity_search
            # results = db_handler.similarity_search(
            #     query=search_words, with_score=True, k=100
            # )

            #2 similarity_search_by_vector
            results = db_handler.similarity_search_by_vector(search_words)

            # # 3 similarity_search_by_vector_with_relevance_scores
            # # 3.1. Получаем эмбеддинг из текста
            # embedding = db_handler.embedding_model.embed_query(search_words)
            # # 3.2. Поиск по эмбеддингу
            # results = db_handler.similarity_search_by_vector_with_relevance_scores(embedding, k=100)

            formatted_results = [
                {
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": score,
                }
                for doc, score in results if score  # убираем None
            ]

            grouped_results = defaultdict(list)
            for r in formatted_results:
                doc_id = r["metadata"].get("document_id", "unknown")
                grouped_results[doc_id].append(r)

            top_decisions = sorted(
                grouped_results.items(),
                key=lambda item: max(r["similarity_score"] for r in item[1]),
                reverse=True
            )

            # Приводим к удобному формату
            result_data = []
            for doc_id, chunks in top_decisions:
                result_data.append({
                    "decision_id": doc_id,
                    "max_score": max(r["similarity_score"] for r in chunks),
                    "chunks": chunks
                })

            return Response({"result": result_data}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Search failed")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class SearchView(APIView):
#     def post(self, request):
#         search_words = request.data.get("search")
#
#         if not search_words or not search_words.strip():
#             return Response({"error": "You need to pass a few key words."}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             # Инициализация Chroma и модели
#             db_handler = ChromaDBHandler()
#             db_handler.init_embedding_model()
#
#             # Синхронный поиск
#             results = db_handler.similarity_search(
#                 query=search_words, with_score=True, k=20
#             )
#             #print(results)
#
#             formatted_results = [
#                 {
#                     "text": doc.page_content,
#                     "metadata": doc.metadata,
#                     "similarity_score": score,
#                 }
#                 for doc, score in results
#             ]
#
#             formatted_results = sorted(
#                 [r for r in formatted_results if r["similarity_score"]],
#                 key=lambda r: r["similarity_score"],
#                 reverse=True
#             )
#             return Response({"result": formatted_results}, status=status.HTTP_200_OK)
#
#             # formatted_results = sorted(
#             #     [r for r in formatted_results if r["similarity_score"] >= 0.65],
#             #     key=lambda r: r["similarity_score"],
#             #     reverse=True
#             # )
#             #
#             # top_results = formatted_results[:5]
#             #
#             # if not top_results or top_results[0]["similarity_score"] < 0.5:
#             #     return Response({"warning": "No relevant results found."}, status=status.HTTP_200_OK)
#             #
#             # return Response({"result": top_results}, status=status.HTTP_200_OK)
#
#         except Exception as e:
#             logger.exception("Search failed")
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

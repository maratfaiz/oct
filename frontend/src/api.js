const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function uploadImage(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/images/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "Не удалось загрузить изображение");
  }

  return response.json();
}

export async function getStatus(imageId) {
  const response = await fetch(`${API_BASE_URL}/api/images/${imageId}/status`);
  if (!response.ok) throw new Error("Не удалось получить статус");
  return response.json();
}

export async function getResult(imageId) {
  const response = await fetch(`${API_BASE_URL}/api/images/${imageId}/result`);
  if (!response.ok) throw new Error("Не удалось получить результат");
  return response.json();
}

export async function analyzeImage(file, { onStatusChange } = {}) {
  const { image_id: imageId, status: initialStatus } = await uploadImage(file);

  let status = initialStatus;
  while (status !== "done") {
    onStatusChange?.(status);
    await new Promise((resolve) => setTimeout(resolve, 1000));
    ({ status } = await getStatus(imageId));
  }

  const result = await getResult(imageId);
  return { imageId, ...result };
}

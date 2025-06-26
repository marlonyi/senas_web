import React from 'react';

export default function PerfilTarjeta({ formData }) {
    return (
        <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-lg overflow-hidden grid grid-cols-1 md:grid-cols-3">
            <div className="bg-blue-700 text-white p-6 flex flex-col items-center justify-center">
                <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center text-blue-700 text-3xl font-bold">
                    {formData.first_name?.charAt(0)}{formData.last_name?.charAt(0)}
                </div>
                <h2 className="mt-4 text-xl font-bold">{formData.first_name} {formData.last_name}</h2>
                <p className="text-blue-200">{formData.email}</p>
            </div>

            <div className="col-span-2 p-6 space-y-4">
                <h3 className="text-lg font-semibold text-gray-800 border-b pb-2">Información Personal</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                        <strong>Teléfono:</strong> {formData.telefono || 'N/D'}
                    </div>
                    <div>
                        <strong>Ciudad:</strong> {formData.ciudad || 'N/D'}
                    </div>
                    <div>
                        <strong>País:</strong> {formData.pais || 'N/D'}
                    </div>
                    <div>
                        <strong>Ocupación:</strong> {formData.ocupacion || 'N/D'}
                    </div>
                    <div>
                        <strong>Nivel Educativo:</strong> {formData.nivel_educativo || 'N/D'}
                    </div>
                    <div>
                        <strong>Idioma Preferido:</strong> {formData.idioma_preferido || 'N/D'}
                    </div>
                </div>

                <h3 className="text-lg font-semibold text-gray-800 border-b pb-2 mt-6">Biografía</h3>
                <p className="text-gray-600 text-sm">{formData.biografia || 'No has escrito una biografía.'}</p>

                <h3 className="text-lg font-semibold text-gray-800 border-b pb-2 mt-6">Accesibilidad</h3>
                <div className="text-sm text-gray-700">
                    <p><strong>Tamaño de fuente:</strong> {formData.preferencias_accesibilidad?.tamano_fuente}</p>
                    <p><strong>Transcripciones activas:</strong> {formData.preferencias_accesibilidad?.transcripciones_activas ? 'Sí' : 'No'}</p>
                    <p><strong>Contraste alto:</strong> {formData.preferencias_accesibilidad?.contraste_alto ? 'Sí' : 'No'}</p>
                </div>
            </div>
        </div>
    );
}
